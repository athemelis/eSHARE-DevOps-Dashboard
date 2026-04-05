// Capacity Planning Data Module - v140

/**
 * Calculate team capacity for a given iteration
 * Capacity = Active Team Members × Working Days in Iteration
 *
 * @param {Object} orgChart - Org chart data from "Org Chart.json"
 * @param {string} iterationPath - Iteration path (e.g., "CY2026Q1-Jan")
 * @returns {Object} Team capacities keyed by team name
 * @example
 * // Returns:
 * {
 *   Frontend: { members: 5, workingDays: 22, totalCapacity: 110, memberNames: [...] },
 *   Backend: { members: 4, workingDays: 22, totalCapacity: 88, memberNames: [...] },
 *   ...
 * }
 */
function calculateTeamCapacity(orgChart, iterationPath) {
    const result = {};

    if (!orgChart || !iterationPath) return result;

    // Parse iteration to get date range
    const { start, end } = parseIterationToDates(iterationPath);
    const workingDays = getWorkingDays(start, end);

    // orgData is array of team objects: { lead, team, members: [...] }
    // Flatten all members arrays to get individual people
    const allMembers = orgChart.flatMap(t => t.members || []);

    // Group employed members by team with their capacity values
    const teamMembers = {};
    allMembers.forEach(person => {
        if (person.status === 'Employed' && person.team) {
            if (!teamMembers[person.team]) {
                teamMembers[person.team] = [];
            }
            // Use capacity field if available, default to 1.0 for backwards compatibility
            const memberCapacity = person.capacity !== undefined ? person.capacity : 1.0;
            teamMembers[person.team].push({
                name: person.name,
                capacity: memberCapacity
            });
        }
    });

    // Calculate capacity for each team using individual member capacities
    Object.entries(teamMembers).forEach(([team, members]) => {
        // Sum individual capacities (each member contributes capacity × workingDays)
        const totalCapacityFTE = members.reduce((sum, m) => sum + m.capacity, 0);
        result[team] = {
            members: members.length,
            workingDays: workingDays,
            totalCapacity: totalCapacityFTE * workingDays,
            memberNames: members.map(m => m.name),
            // Include FTE breakdown for debugging/display
            totalFTE: totalCapacityFTE
        };
    });

    return result;
}

/**
 * Get planned effort for a Feature by aggregating its Delivery Slices
 * Only includes Delivery Slices matching the selected iteration
 *
 * @param {Object} feature - Feature work item
 * @param {string} iterationPath - Iteration path to filter slices
 * @param {Array} workItemLinks - Links from "WorkItemLinks.json"
 * @param {Array} allItems - All work items from "ALL Items.json"
 * @returns {Object} Effort breakdown by team
 * @example
 * // Returns:
 * {
 *   total: 45,
 *   teamEfforts: { Frontend: 15, Backend: 20, QA: 10 },
 *   teamSliceCounts: { Frontend: 2, Backend: 1, QA: 1 },
 *   deliverySlices: [...]
 * }
 */
function getFeatureEffort(feature, iterationPath, workItemLinks, allItems) {
    const result = {
        total: 0,
        teamEfforts: {},
        teamSliceCounts: {},
        deliverySlices: []
    };

    if (!feature || !workItemLinks || !allItems) return result;

    // Find child Delivery Slices via hierarchy links
    // Link format: { source: parentId, target: childId, type: 'Child' }
    const childIds = workItemLinks
        .filter(link =>
            link.source === feature.id &&
            link.type === 'Child'
        )
        .map(link => link.target);

    const allChildIds = new Set(childIds);

    // Get Delivery Slices that match the iteration
    const deliverySlices = allItems.filter(item =>
        allChildIds.has(item.id) &&
        item.type === 'Delivery Slice' &&
        matchesIteration(item, iterationPath)
    );

    result.deliverySlices = deliverySlices;

    // Aggregate effort by team
    deliverySlices.forEach(slice => {
        // Extract team from areaPath (last segment)
        const team = slice.areaPath ? slice.areaPath.split('\\').pop() : 'Unknown';
        const effort = slice.effort || 0;

        if (!result.teamEfforts[team]) {
            result.teamEfforts[team] = 0;
            result.teamSliceCounts[team] = 0;
        }

        result.teamEfforts[team] += effort;
        result.teamSliceCounts[team] += 1;
        result.total += effort;
    });

    return result;
}

/**
 * Get planned effort for a Bug from its team estimation fields
 * Fields: frontendEstimation, backendEstimation, qaEstimation,
 *         devopsEstimation, analyticsEstimation, governEstimation, scgEstimation
 *
 * @param {Object} bug - Bug work item
 * @param {string} iterationPath - Iteration path (for validation)
 * @returns {Object} Effort breakdown by team
 * @example
 * // Returns:
 * {
 *   total: 12,
 *   teamEfforts: { Backend: 8, QA: 4 }
 * }
 */
function getBugEffort(bug, iterationPath) {
    const result = {
        total: 0,
        teamEfforts: {}
    };

    if (!bug) return result;

    // Validate bug matches iteration (if iterationPath provided)
    if (iterationPath && !matchesIteration(bug, iterationPath)) {
        return result;
    }

    // Map estimation fields to team names
    const fieldToTeam = {
        frontendEstimation: 'Frontend',
        backendEstimation: 'Backend',
        qaEstimation: 'QA',
        devopsEstimation: 'DevOps',
        analyticsEstimation: 'Analytics',
        governEstimation: 'Govern',
        scgEstimation: 'SCG'
    };

    // Extract effort from each field
    Object.entries(fieldToTeam).forEach(([field, team]) => {
        const effort = parseFloat(bug[field]) || 0;
        if (effort > 0) {
            result.teamEfforts[team] = effort;
            result.total += effort;
        }
    });

    return result;
}

/**
 * Calculate completion percentage from actual vs planned effort
 *
 * @param {number} actualEffort - Completed work (from child Tasks)
 * @param {number} plannedEffort - Planned effort (from Delivery Slices or Bug estimates)
 * @returns {number} Completion percentage (0-100+, can exceed 100 if over-delivered)
 * @example
 * calculateCompletion(18, 32) // Returns 56
 * calculateCompletion(40, 40) // Returns 100
 * calculateCompletion(0, 0)   // Returns 0 (avoid division by zero)
 */
function calculateCompletion(actualEffort, plannedEffort) {
    if (!plannedEffort || plannedEffort === 0) return 0;
    return Math.round((actualEffort / plannedEffort) * 100);
}

/**
 * Calculate working days between two dates (excluding weekends)
 * Used to determine iteration capacity
 *
 * @param {Date} startDate - Iteration start date
 * @param {Date} endDate - Iteration end date
 * @returns {number} Number of working days (Mon-Fri)
 * @example
 * // January 2026 has 22 working days
 * getWorkingDays(new Date(2026, 0, 1), new Date(2026, 0, 31)) // Returns 22
 */
function getWorkingDays(startDate, endDate) {
    if (!startDate || !endDate) return 0;
    let count = 0;
    const current = new Date(startDate);
    while (current <= endDate) {
        const dayOfWeek = current.getDay();
        if (dayOfWeek !== 0 && dayOfWeek !== 6) {
            count++;
        }
        current.setDate(current.getDate() + 1);
    }
    return count;
}

/**
 * Parse iteration string to start/end dates
 * Format: "CY{year}Q{quarter}-{month}" → { startDate, endDate }
 *
 * @param {string} iteration - Iteration string (e.g., "CY2026Q1-Jan")
 * @returns {Object} { startDate: Date, endDate: Date } or nulls if invalid
 * @example
 * parseIterationToDates("CY2026Q1-Jan")
 * // Returns { startDate: Jan 1 2026, endDate: Jan 31 2026 }
 */
function parseIterationToDates(iteration) {
    if (!iteration || typeof iteration !== 'string') return { start: null, end: null };

    // Pattern: CY{year}Q{quarter}-{month}
    const match = iteration.match(/CY(\d{4})Q(\d)-(\w+)/);
    if (!match) return { start: null, end: null };

    const year = parseInt(match[1]);
    const monthName = match[3];

    const monthMap = {
        'Jan': 0, 'Feb': 1, 'Mar': 2,
        'Apr': 3, 'May': 4, 'Jun': 5,
        'Jul': 6, 'Aug': 7, 'Sep': 8,
        'Oct': 9, 'Nov': 10, 'Dec': 11
    };

    const month = monthMap[monthName];
    if (month === undefined) return { start: null, end: null };

    const start = new Date(year, month, 1);
    const end = new Date(year, month + 1, 0); // Last day of month

    return { start, end };
}

/**
 * Check if a work item matches the selected iteration
 *
 * @param {Object} workItem - Work item to check
 * @param {string} selectedIteration - Iteration to match (e.g., "CY2026Q1-Jan")
 * @returns {boolean} True if work item is in the selected iteration
 */
function matchesIteration(workItem, selectedIteration) {
    if (!selectedIteration) return false;

    // Handle "(No Iteration)" filter
    if (selectedIteration === '(No Iteration)') {
        return !workItem.iterationPath || workItem.iterationPath === '';
    }

    // Extract last segment from iteration path (e.g., "eShare\\CY2026Q1-Jan" → "CY2026Q1-Jan")
    const itemIteration = workItem.iterationPath
        ? workItem.iterationPath.split('\\').pop()
        : '';

    return itemIteration === selectedIteration;
}

/**
 * Get actual effort (completed work) from child Tasks
 *
 * @param {Object} parentItem - Parent work item (Feature or Bug)
 * @param {Array} workItemLinks - Links from "WorkItemLinks.json"
 * @param {Array} allItems - All work items from "ALL Items.json"
 * @returns {number} Sum of completedWork from child Tasks
 */
function getActualEffort(parentItem, workItemLinks, allItems) {
    if (!parentItem || !workItemLinks || !allItems) return 0;

    // Find child Tasks via hierarchy links
    // Link format: { source: parentId, target: childId, type: 'Child' }
    const childIds = workItemLinks
        .filter(link =>
            link.source === parentItem.id &&
            link.type === 'Child'
        )
        .map(link => link.target);

    const allChildIds = new Set(childIds);

    // Get Tasks and sum completedWork
    const tasks = allItems.filter(item =>
        allChildIds.has(item.id) && item.type === 'Task'
    );

    return tasks.reduce((sum, task) => sum + (task.completedWork || 0), 0);
}

// Module export
window.capacityPlanningData = {
    calculateTeamCapacity,
    getFeatureEffort,
    getBugEffort,
    calculateCompletion,
    getWorkingDays,
    parseIterationToDates,
    matchesIteration,
    getActualEffort
};

// ============================================================
// Test Examples (run in browser console to verify)
// ============================================================
function runCapacityDataTests() {
    console.log('=== Capacity Planning Data Tests ===\n');

    // Test parseIterationToDates
    console.log('parseIterationToDates("CY2026Q1-Jan"):');
    const jan2026 = parseIterationToDates('CY2026Q1-Jan');
    console.log('  start:', jan2026.start?.toDateString()); // Thu Jan 01 2026
    console.log('  end:', jan2026.end?.toDateString());     // Sat Jan 31 2026

    console.log('parseIterationToDates("CY2025Q4-Dec"):');
    const dec2025 = parseIterationToDates('CY2025Q4-Dec');
    console.log('  start:', dec2025.start?.toDateString()); // Mon Dec 01 2025
    console.log('  end:', dec2025.end?.toDateString());     // Wed Dec 31 2025

    console.log('parseIterationToDates("invalid"):');
    const invalid = parseIterationToDates('invalid');
    console.log('  start:', invalid.start); // null
    console.log('  end:', invalid.end);     // null

    // Test getWorkingDays
    console.log('\ngetWorkingDays for January 2026:');
    const workDays = getWorkingDays(jan2026.start, jan2026.end);
    console.log('  working days:', workDays); // 22 (Jan 2026 has 22 weekdays)

    console.log('getWorkingDays for December 2025:');
    const decDays = getWorkingDays(dec2025.start, dec2025.end);
    console.log('  working days:', decDays); // 23 (Dec 2025 has 23 weekdays)

    // Test matchesIteration
    console.log('\nmatchesIteration tests:');
    const item1 = { iterationPath: 'eShare\\CY2026Q1-Jan' };
    const item2 = { iterationPath: 'eShare\\CY2025Q4-Dec' };
    const item3 = { iterationPath: '' };

    console.log('  item with CY2026Q1-Jan matches "CY2026Q1-Jan":', matchesIteration(item1, 'CY2026Q1-Jan')); // true
    console.log('  item with CY2025Q4-Dec matches "CY2026Q1-Jan":', matchesIteration(item2, 'CY2026Q1-Jan')); // false
    console.log('  item with empty path matches "(No Iteration)":', matchesIteration(item3, '(No Iteration)')); // true

    // Test calculateCompletion
    console.log('\ncalculateCompletion tests:');
    console.log('  18/32:', calculateCompletion(18, 32), '% (expected 56)');
    console.log('  40/40:', calculateCompletion(40, 40), '% (expected 100)');
    console.log('  0/0:', calculateCompletion(0, 0), '% (expected 0)');
    console.log('  50/40:', calculateCompletion(50, 40), '% (expected 125 - over delivery)');

    // Test getBugEffort
    console.log('\ngetBugEffort tests:');
    const testBug = {
        id: 123,
        type: 'Bug',
        iterationPath: 'eShare\\CY2026Q1-Jan',
        frontendEstimation: 5,
        backendEstimation: 8,
        qaEstimation: 3,
        devopsEstimation: null,
        analyticsEstimation: 0
    };
    const bugEffort = getBugEffort(testBug, 'CY2026Q1-Jan');
    console.log('  Bug effort:', bugEffort);
    console.log('  Expected: { total: 16, teamEfforts: { Frontend: 5, Backend: 8, QA: 3 } }');

    // Test getFeatureEffort (mock data)
    console.log('\ngetFeatureEffort tests:');
    const testFeature = { id: 100, type: 'Feature' };
    const testLinks = [
        { sourceId: 100, targetId: 201, linkType: 'System.LinkTypes.Hierarchy-Forward' },
        { sourceId: 100, targetId: 202, linkType: 'System.LinkTypes.Hierarchy-Forward' }
    ];
    const testItems = [
        { id: 201, type: 'Delivery Slice', iterationPath: 'eShare\\CY2026Q1-Jan', areaPath: 'eShare\\Frontend', effort: 10 },
        { id: 202, type: 'Delivery Slice', iterationPath: 'eShare\\CY2026Q1-Jan', areaPath: 'eShare\\Backend', effort: 15 }
    ];
    const featureEffort = getFeatureEffort(testFeature, 'CY2026Q1-Jan', testLinks, testItems);
    console.log('  Feature effort:', featureEffort);
    console.log('  Expected total: 25, Frontend: 10, Backend: 15');

    // Test getActualEffort (mock data)
    console.log('\ngetActualEffort tests:');
    const testParent = { id: 201, type: 'Delivery Slice' };
    const testTaskLinks = [
        { sourceId: 201, targetId: 301, linkType: 'System.LinkTypes.Hierarchy-Forward' },
        { sourceId: 201, targetId: 302, linkType: 'System.LinkTypes.Hierarchy-Forward' }
    ];
    const testTaskItems = [
        { id: 301, type: 'Task', completedWork: 4 },
        { id: 302, type: 'Task', completedWork: 6 }
    ];
    const actualEffort = getActualEffort(testParent, testTaskLinks, testTaskItems);
    console.log('  Actual effort:', actualEffort, '(expected 10)');

    // Test calculateTeamCapacity (mock org chart)
    console.log('\ncalculateTeamCapacity tests:');
    const mockOrgChart = [
        { name: 'Alice', team: 'Frontend', status: 'Active' },
        { name: 'Bob', team: 'Frontend', status: 'Active' },
        { name: 'Carol', team: 'Frontend', status: 'Active' },
        { name: 'Dave', team: 'Frontend', status: 'Active' },
        { name: 'Eve', team: 'Frontend', status: 'Active' },
        { name: 'Frank', team: 'Backend', status: 'Active' },
        { name: 'Grace', team: 'Backend', status: 'Active' },
        { name: 'Hank', team: 'Backend', status: 'Active' },
        { name: 'Ivy', team: 'Backend', status: 'Former' }, // Should be excluded
        { name: 'Jack', team: 'QA', status: 'Active' }
    ];
    const teamCapacity = calculateTeamCapacity(mockOrgChart, 'CY2026Q1-Jan');
    console.log('  Team capacities:', teamCapacity);
    console.log('  Expected: Frontend: 5×22=110, Backend: 3×22=66, QA: 1×22=22');

    console.log('\n=== Tests Complete ===');
}

// Expose test function
window.runCapacityDataTests = runCapacityDataTests;
