// ============================================================
// eShare DevOps Dashboard - Data Loader Module
// ============================================================
// This module handles loading JSON data from SharePoint and
// transforming it for use by the dashboard.
// ============================================================

(function (window) {
  "use strict";

  // Detect if running on localhost (skip MSAL auth for local development)
  const isLocalhost =
    window.location.hostname === "localhost" ||
    window.location.hostname === "127.0.0.1";

  // Configuration - paths relative to SharePoint document library
  const CONFIG = {
    DATA_BASE_URL: "", // Will be set based on current location
    ALL_ITEMS_FILE: "ALL Items.json",
    WORK_ITEM_LINKS_FILE: "WorkItemLinks.json",
    ORG_CHART_FILE: "Org Chart.json",
    REFRESH_INTERVAL_MS: 60000, // 60 seconds
    ADO_BASE_URL: "https://dev.azure.com/ncryptedcloud/eShare/_workitems/edit/",

    // SharePoint file IDs (resilient to file renames)
    // Site: wardedbox.sharepoint.com/sites/ProductManagement
    // Folder: Product Planning
    SHAREPOINT: {
      SITE_ID: "wardedbox.sharepoint.com,068d0a61-5001-4876-9b1f-aca355308c6e,93466068-93c9-4528-bfc4-9e999b2f9980",
      DRIVE_ID: "b!YQqNBgFQdkibH6yjVTCMbmhgRpPJkyhFv8SemZsvmYDmzFMoAwiJQbOxeixmqlX1",
      FILES: {
        ALL_ITEMS: "01VN5XFOTKZ2ORQHSSKFF3XBLIMIFJ7W6Z",
        WORK_ITEM_LINKS: "01VN5XFOTVIBXRISXZ4RAKUOWMG4KTXRY6",
        ORG_CHART: "01VN5XFOTIJDORTXW4LVA35BIQVR35ZPAR",
        CASCADING_LISTS: "01VN5XFORERWFTAPDJ7NAKVH3JLZW6BFOA",
      }
    }
  };

  // MSAL variables (only initialized for non-localhost)
  let msalInstance = null;
  let loginRequest = null;
  let tokenRequest = null;
  let adoTokenRequest = null;

  // Only initialize MSAL if NOT on localhost
  if (!isLocalhost) {
    // Redirect URI for production domain

    // MSAL Configuration
    const msalConfig = {
      auth: {
        clientId: "bf683b68-0dc3-4205-a5b7-676f54a958c0",
        authority:
          "https://login.microsoftonline.com/wardedbox.onmicrosoft.com",
        redirectUri: window.location.origin + window.location.pathname,
      },
      cache: {
        cacheLocation: "localStorage",
        storeAuthStateInCookie: false,
        navigateToLoginRequestUrl: false,
      },
    };

    // Create MSAL instance
    msalInstance = new msal.PublicClientApplication(msalConfig);

    // Request configuration for SharePoint
    // Sites.Selected restricts access to only the specific SharePoint sites
    // that have been explicitly granted to the app registration
    loginRequest = {
      scopes: ["Sites.Selected"],
    };

    tokenRequest = {
      scopes: ["Sites.Selected"],
    };

    // Azure DevOps token request (user_impersonation scope)
    adoTokenRequest = {
      scopes: ["499b84ac-1321-427f-aa17-267ca6975798/user_impersonation"],
    };

    // Initialize
    msalInstance.initialize().then(() => {
      // Handle redirect promise
      msalInstance
        .handleRedirectPromise()
        .then(handleResponse)
        .catch((err) => {
          console.error(err);
        });

      // Check if user is already signed in
      checkAccount();
    });
  } else {
    console.log("Running on localhost - MSAL authentication disabled");
  }

  function checkAccount() {
    const accounts = msalInstance.getAllAccounts();
    if (accounts.length > 0) {
      msalInstance.setActiveAccount(accounts[0]);
    }
  }

  function handleResponse(response) {
    if (response) {
      msalInstance.setActiveAccount(response.account);
    }
  }

  function handleResponseNew(response) {
    const loginRequest = {
      scopes: ["Sites.Selected"],
    };

    let accountId = null;

    if (response !== null) {
      accountId = response.account.homeAccountId;
      // reload to make sure Sharepoint data is loaded correctly
      window.location.reload();
    } else {
      // In case multiple accounts exist, you can select
      const currentAccounts = msalInstance.getAllAccounts();

      if (currentAccounts.length === 0) {
        // no accounts signed-in, attempt to sign a user in
        msalInstance.loginRedirect(loginRequest);
      } else if (currentAccounts.length > 1) {
        // Add choose account code here
      } else if (currentAccounts.length === 1) {
        accountId = currentAccounts[0].homeAccountId;
      }
    }
  }

  async function signIn() {
    if (isLocalhost || !msalInstance) {
      console.log("Localhost mode - no authentication required");
      return;
    }
    try {
      msalInstance.handleRedirectPromise().then(handleResponseNew);
    } catch (error) {
      console.error("Login error:", error);
    }
  }

  async function signOut() {
    if (isLocalhost || !msalInstance) {
      console.log("Localhost mode - no logout required");
      return;
    }
    const account = msalInstance.getActiveAccount();
    if (account) {
      try {
        const logoutRequest = {
          account: msalInstance.getAccountByHomeId(account.homeAccountId),
        };
        msalInstance.logoutRedirect(logoutRequest);
      } catch (error) {
        console.error("Logout error:", error);
      }
    }
  }

  // Get access token for Graph API calls
  async function getAccessToken() {
    const account = msalInstance.getActiveAccount();
    if (!account) {
      throw new Error("No active account - user must sign in");
    }

    try {
      const response = await msalInstance.acquireTokenSilent({
        ...tokenRequest,
        account: account,
      });
      return response.accessToken;
    } catch (error) {
      console.warn("Silent token acquisition failed, trying interactive:", error);
      await msalInstance.acquireTokenRedirect(tokenRequest);
      // After this call, the browser will redirect and execution will not continue.
      throw new Error("Redirecting for interactive authentication – token will be handled via handleRedirectPromise().");
    }
  }

  // Get access token for Azure DevOps API calls
  async function getAdoAccessToken() {
    if (isLocalhost || !msalInstance) return null;

    const account = msalInstance.getActiveAccount();
    if (!account) return null;

    try {
      const response = await msalInstance.acquireTokenSilent({
        ...adoTokenRequest,
        account: account,
      });
      return response.accessToken;
    } catch (error) {
      console.warn("ADO silent token acquisition failed:", error);
      return null;
    }
  }

  // Fetch SharePoint file by ID (resilient to renames)
  async function getSharePointFileById(fileId, fileName) {
    const account = msalInstance.getActiveAccount();
    if (!account) {
      return { data: [], lastModified: null };
    }

    try {
      const accessToken = await getAccessToken();

      // First, get the file metadata including the download URL
      // The /content endpoint returns a 302 redirect which causes CORS issues
      // Instead, we get the @microsoft.graph.downloadUrl which supports CORS
      const metadataUrl = `https://graph.microsoft.com/v1.0/sites/${CONFIG.SHAREPOINT.SITE_ID}/drive/items/${fileId}?select=id,name,@microsoft.graph.downloadUrl,lastModifiedDateTime`;

      console.log(`Fetching ${fileName} metadata by ID:`, fileId);

      const metadataResponse = await fetch(metadataUrl, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });

      if (!metadataResponse.ok) {
        const errorText = await metadataResponse.text();
        throw new Error(
          `Failed to get metadata for ${fileName}: ${metadataResponse.status} ${metadataResponse.statusText}\n${errorText}`,
        );
      }

      const metadata = await metadataResponse.json();
      const downloadUrl = metadata["@microsoft.graph.downloadUrl"];
      const lastModified = metadata.lastModifiedDateTime;

      if (!downloadUrl) {
        throw new Error(`No download URL available for ${fileName}`);
      }

      console.log(`Downloading ${fileName} from pre-authenticated URL`);

      // Fetch the actual file content using the pre-authenticated download URL
      // This URL already has auth embedded, so no Authorization header needed
      const fileResponse = await fetch(downloadUrl);

      if (!fileResponse.ok) {
        throw new Error(
          `Failed to download ${fileName}: ${fileResponse.status} ${fileResponse.statusText}`,
        );
      }

      // Get the file content
      const data = await fileResponse.json();

      return { data, lastModified };
    } catch (error) {
      console.error(`Error fetching SharePoint file ${fileName}:`, error);
      throw error;
    }
  }

  // Legacy function: Fetch SharePoint file by path (kept for backwards compatibility)
  async function getSharePointFile(
    siteHostname,
    sitePath,
    folderPath,
    fileName,
  ) {
    const account = msalInstance.getActiveAccount();
    if (!account) {
      return { data: [], lastModified: null };
    }

    try {
      const accessToken = await getAccessToken();

      // First, get the site ID
      const siteUrl = `https://graph.microsoft.com/v1.0/sites/${siteHostname}:${sitePath}`;
      const siteResponse = await fetch(siteUrl, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });

      if (!siteResponse.ok) {
        const errorText = await siteResponse.text();
        throw new Error(
          `Failed to get site: ${siteResponse.status} ${siteResponse.statusText}\n${errorText}`,
        );
      }

      const siteData = await siteResponse.json();
      const siteId = siteData.id;

      // Get the file content using Graph API
      // URL-encode the folder path and file name to handle spaces and special characters
      const encodedFolderPath = folderPath.split('/').map(encodeURIComponent).join('/');
      const encodedFileName = encodeURIComponent(fileName);
      const fileUrl = `https://graph.microsoft.com/v1.0/sites/${siteId}/drive/root:/${encodedFolderPath}/${encodedFileName}:/content`;

      console.log("Fetching file from:", fileUrl);

      const fileResponse = await fetch(fileUrl, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });

      if (!fileResponse.ok) {
        const errorText = await fileResponse.text();
        throw new Error(
          `Failed to fetch ${fileName}: ${fileResponse.status} ${fileResponse.statusText}\n${errorText}`,
        );
      }

      // Get the file content
      const data = await fileResponse.json();

      const lastModified = fileResponse.headers.get("Last-Modified");

      return { data, lastModified };
    } catch (error) {
      console.error("Error fetching SharePoint files:", error);
      throw error;
    }
  }

  // Determine base URL based on current location
  function getBaseUrl() {
    const hostname = window.location.hostname;
    const path = window.location.pathname;

    // If running from SharePoint, use relative path
    if (
      hostname.includes("sharepoint.com") ||
      path.includes("Product Planning")
    ) {
      return "./";
    }

    // Local development via http server - use relative path (files in same directory)
    if (hostname === "localhost" || hostname === "127.0.0.1") {
      return "./";
    }

    // File protocol - use SharePoint path via OneDrive sync
    return "/Users/tonythem/Library/CloudStorage/OneDrive-SharedLibraries-e-Share/Product Management - Documents/Product Planning/";
  }

  // Transform raw JSON field names to dashboard-friendly names
  // This handles the mapping from ADO Analytics API field names
  function transformWorkItem(item) {
    return {
      id: item.id,
      type: item.type,
      title: item.title,
      state: item.state,
      assignedTo: item.assignedTo || "",
      areaPath: item.areaPath || "",
      iterationPath: item.iterationPath || "",
      createdDate: item.createdDate,
      closedDate: convertUtcToAthensDate(item.closedDate),
      stateChangeDate: item.stateChangeDate,
      targetDate: convertUtcToAthensDate(item.targetDate),
      priority: item.priority,
      severity: item.severity,
      tags: item.tags || "",
      parentId: item.parentId,
      effort: item.effort,
      effortRollup: item.effortRollup,
      originalEstimate: item.originalEstimate,
      backlogPriority: item.backlogPriority,
      customers: item.customers || "",
      teamsAffected: item.teamsAffected || "",
      releaseVersion: item.releaseVersion || "",
      bugType: item.bugType || "",
      component: item.component || "",
      feature: item.feature || "",
      ticketCategory: item.ticketCategory || "",
      deliverySliceOwner: item.deliverySliceOwner || "",
      csOwner: item.csOwner || "",
      workLogData: item.workLogData || "",
      taskType: item.taskType || "",
      // Bug-specific boolean fields
      security: item.security,
      regression: item.regression,
      // Capacity Planning fields (v143+)
      committedIterations: item.committedIterations || "",
      analyticsEstimation: item.analyticsEstimation || null,
      backendEstimation: item.backendEstimation || null,
      devopsEstimation: item.devopsEstimation || null,
      frontendEstimation: item.frontendEstimation || null,
      governEstimation: item.governEstimation || null,
      scgEstimation: item.scgEstimation || null,
      qaEstimation: item.qaEstimation || null,
      staffEstimation: item.staffEstimation || null,
      // v155: Cascading fields (replacing releaseVersion/targetDate)
      cascadingVersion: item.cascadingVersion || "",
      cascadingDate: item.cascadingDate || "",
      // Derived fields
      team: extractTeamFromAreaPath(item.areaPath),
      iteration: extractIterationFromPath(item.iterationPath),
      url: CONFIG.ADO_BASE_URL + item.id,
    };
  }

  // Extract team name from area path (e.g., "eShare\\Frontend" -> "Frontend")
  function extractTeamFromAreaPath(areaPath) {
    if (!areaPath) return "";
    const parts = areaPath.split("\\");
    return parts.length > 1 ? parts[parts.length - 1] : parts[0];
  }

  // Extract iteration from iteration path (e.g., "eShare\\CY2025Q4-Dec" -> "CY2025Q4-Dec")
  function extractIterationFromPath(iterationPath) {
    if (!iterationPath) return "";
    const parts = iterationPath.split("\\");
    return parts.length > 1 ? parts[parts.length - 1] : parts[0];
  }

  // Convert UTC date-only field to Athens timezone date
  // ADO stores date-only fields (like TargetDate, ClosedDate) as midnight in Athens timezone.
  // Power Automate exports convert this to UTC, which shifts the date back.
  // Example: Dec 11 midnight Athens = Dec 10 22:00 UTC = "2025-12-10T22:00:00Z"
  // We convert back to Athens to get the intended date.
  function convertUtcToAthensDate(isoString) {
    if (!isoString) return null;
    try {
      // Parse the UTC date
      const utcDate = new Date(isoString);
      if (isNaN(utcDate.getTime())) return isoString;

      // Convert to Athens timezone and extract date
      const athensDate = utcDate.toLocaleDateString("en-CA", {
        timeZone: "Europe/Athens",
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
      });
      return athensDate; // Returns YYYY-MM-DD format
    } catch (e) {
      return isoString;
    }
  }

  // Transform work item link from JSON format
  function transformWorkItemLink(link) {
    return {
      source: link.source,
      target: link.target,
      type: link.type,
      comment: link.comment || "",
    };
  }

  // Parse CSV text into array of objects
  function parseCSV(csvText) {
    // Remove BOM (Byte Order Mark) if present - common in Excel-exported CSVs
    if (csvText.charCodeAt(0) === 0xfeff) {
      csvText = csvText.slice(1);
    }

    const lines = csvText.split("\n").filter((line) => line.trim());
    if (lines.length === 0) return [];

    // Parse header row
    const headers = parseCSVLine(lines[0]);

    // Parse data rows
    const rows = [];
    for (let i = 1; i < lines.length; i++) {
      const values = parseCSVLine(lines[i]);
      const row = {};
      headers.forEach((header, idx) => {
        row[header.trim()] = (values[idx] || "").trim();
      });
      rows.push(row);
    }
    return rows;
  }

  // Parse a single CSV line, handling quoted values
  function parseCSVLine(line) {
    const values = [];
    let current = "";
    let inQuotes = false;

    for (let i = 0; i < line.length; i++) {
      const char = line[i];
      if (char === '"') {
        inQuotes = !inQuotes;
      } else if (char === "," && !inQuotes) {
        values.push(current);
        current = "";
      } else {
        current += char;
      }
    }
    values.push(current);
    return values;
  }

  // Process org chart CSV into the expected format
  // Output: [{ lead: 'Name', team: 'Team1 & Team2', members: [{ name: 'Name', team: 'Team', status: 'Status' }] }]
  function processOrgChart(rows) {
    const grouped = {};

    for (const row of rows) {
      const lead = row["Lead"] || "";
      if (!lead) continue;

      if (!grouped[lead]) {
        grouped[lead] = {
          lead: lead,
          teams: new Set(),
          members: [],
        };
      }

      const formalName = row["Formal Name"] || "";
      const commonName = row["Common Name"] || formalName;
      const memberTeam = row["Team"] || "";
      const memberStatus = row["Status"] || "Employed";

      if (commonName && memberTeam) {
        grouped[lead].teams.add(memberTeam);
        const capacity = row["Capacity"] !== undefined ? parseFloat(row["Capacity"]) : 1.0;
        grouped[lead].members.push({
          name: commonName,
          formalName: formalName, // Include formal name for ADO lookup
          team: memberTeam,
          status: memberStatus,
          capacity: capacity, // 0.0-1.0 representing % of time spent coding
          isLead: formalName === lead || commonName === lead, // Flag if this person is the team lead
        });
      }
    }

    // Convert to final format with combined team names
    const result = [];
    for (const lead in grouped) {
      const data = grouped[lead];
      const teamsSorted = [...data.teams].sort();
      const teamLabel =
        teamsSorted.length > 1
          ? teamsSorted.join(" & ")
          : teamsSorted[0] || "Unknown";

      result.push({
        lead: data.lead,
        team: teamLabel,
        members: data.members,
      });
    }

    // Sort by lead name for consistent output
    result.sort((a, b) => a.lead.localeCompare(b.lead));
    return result;
  }

  // Fetch text data (for CSV files)
  async function fetchText(url) {
    const response = await fetch(url, {
      cache: "no-store",
      headers: {
        Accept: "text/csv,text/plain,*/*",
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.text();
  }

  // Fetch JSON data with error handling
  async function fetchJson(url) {
    const response = await fetch(url, {
      cache: "no-store", // Always get fresh data
      headers: {
        Accept: "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    // Get last modified timestamp for display
    const lastModified = response.headers.get("Last-Modified");
    const data = await response.json();

    return { data, lastModified };
  }

  // Cache for storing last successful data (fault resilience)
  let cachedData = null;
  const CACHE_KEY = "dashboardDataCache";

  // Try to load cached data from localStorage
  function loadCachedData() {
    try {
      const cached = localStorage.getItem(CACHE_KEY);
      if (cached) {
        cachedData = JSON.parse(cached);
        console.log("Loaded cached data from localStorage");
      }
    } catch (e) {
      console.warn("Failed to load cached data:", e.message);
    }
    return cachedData;
  }

  // Save data to cache (skip on localhost - local files load fast)
  function saveCachedData(data) {
    // Always update in-memory cache
    cachedData = data;

    // Skip localStorage on localhost (local file loads are fast, no need to cache)
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
      return;
    }

    try {
      const jsonStr = JSON.stringify(data);
      const sizeMB = (jsonStr.length * 2) / (1024 * 1024); // UTF-16 = 2 bytes per char
      if (sizeMB > 4) {
        console.warn(`Cache size (${sizeMB.toFixed(1)}MB) exceeds 4MB limit, skipping localStorage`);
        return;
      }
      localStorage.setItem(CACHE_KEY, jsonStr);
      console.log(`Saved data to cache (${sizeMB.toFixed(1)}MB)`);
    } catch (e) {
      // Silently handle quota exceeded - dashboard works fine without cache
      if (e.name === 'QuotaExceededError') {
        console.warn('localStorage quota exceeded, caching disabled');
      }
    }
  }

  // Retry wrapper with exponential backoff
  async function fetchWithRetry(fetchFn, maxRetries = 3, baseDelayMs = 1000) {
    let lastError;
    for (let attempt = 0; attempt < maxRetries; attempt++) {
      try {
        return await fetchFn();
      } catch (error) {
        lastError = error;
        console.warn(`Fetch attempt ${attempt + 1}/${maxRetries} failed:`, error.message);
        if (attempt < maxRetries - 1) {
          const delay = baseDelayMs * Math.pow(2, attempt);
          console.log(`Retrying in ${delay}ms...`);
          await new Promise(resolve => setTimeout(resolve, delay));
        }
      }
    }
    throw lastError;
  }

  // Load all dashboard data
  async function loadDashboardData(options = {}) {
    const baseUrl = options.baseUrl || getBaseUrl();
    // URL-encode filenames to handle spaces
    const allItemsUrl = baseUrl + encodeURIComponent(CONFIG.ALL_ITEMS_FILE);
    const linksUrl = baseUrl + encodeURIComponent(CONFIG.WORK_ITEM_LINKS_FILE);
    const orgChartUrl = baseUrl + encodeURIComponent(CONFIG.ORG_CHART_FILE);

    // Load cached data as fallback
    const cached = loadCachedData();

    try {
      // Show loading state
      if (options.onLoadStart) {
        options.onLoadStart();
      }

      let itemsResult, linksResult, orgChartResult;

      // Use direct fetch for localhost, SharePoint Graph API for production
      if (isLocalhost) {
        // Local development - fetch JSON files directly with retry
        console.log("Loading data from local files...");
        [itemsResult, linksResult, orgChartResult] = await Promise.all([
          fetchWithRetry(() => fetchJson(allItemsUrl)),
          fetchWithRetry(() => fetchJson(linksUrl)),
          fetchWithRetry(() => fetchJson(orgChartUrl)).catch((err) => {
            console.warn(
              "Org chart not found, continuing without it:",
              err.message,
            );
            return { data: null };
          }),
        ]);
      } else {
        // Production - use SharePoint Graph API with MSAL
        // Fetch by file ID (resilient to file renames)
        const account = msalInstance.getActiveAccount();
        if (!account) {
          await signIn();
        }

        console.log("Loading data from SharePoint by file ID...");

        // Fetch all files in parallel by ID with retry (org chart is optional - don't fail if missing)
        [itemsResult, linksResult, orgChartResult] = await Promise.all([
          fetchWithRetry(() => getSharePointFileById(
            CONFIG.SHAREPOINT.FILES.ALL_ITEMS,
            "ALL Items.json",
          )),
          fetchWithRetry(() => getSharePointFileById(
            CONFIG.SHAREPOINT.FILES.WORK_ITEM_LINKS,
            "WorkItemLinks.json",
          )),
          fetchWithRetry(() => getSharePointFileById(
            CONFIG.SHAREPOINT.FILES.ORG_CHART,
            "Org Chart.json",
          )).catch((err) => {
            console.warn(
              "Org chart not found, continuing without it:",
              err.message,
            );
            return { data: null };
          }),
        ]);
      }

      // Transform work items
      const workItems = Array.isArray(itemsResult.data)
        ? itemsResult.data.map(transformWorkItem)
        : [];

      // Transform work item links
      const workItemLinks = Array.isArray(linksResult.data)
        ? linksResult.data.map(transformWorkItemLink)
        : [];

      // Process org chart if available (JSON format: array of row objects)
      let orgChartData = [];
      if (orgChartResult.data && Array.isArray(orgChartResult.data)) {
        orgChartData = processOrgChart(orgChartResult.data);
        console.log(
          `Loaded org chart: ${orgChartData.length} leads, ${orgChartData.reduce((sum, g) => sum + g.members.length, 0)} members`,
        );
      }

      // Get the most recent last-modified timestamp
      const lastModified =
        itemsResult.lastModified ||
        linksResult.lastModified ||
        new Date().toISOString();

      // Generate validation data (source counts)
      const csvValidationData = {
        totalItems: workItems.length,
        byType: {},
      };
      workItems.forEach((item) => {
        csvValidationData.byType[item.type] =
          (csvValidationData.byType[item.type] || 0) + 1;
      });

      const result = {
        workItems,
        workItemLinks,
        orgChartData,
        csvValidationData,
        lastModified,
        success: true,
        fromCache: false,
      };

      // Cache the successful result
      saveCachedData(result);

      return result;
    } catch (error) {
      console.error("Failed to load dashboard data:", error);

      // Return cached data if available (fault resilience)
      if (cached && cached.workItems && cached.workItems.length > 0) {
        console.warn("Using cached data due to fetch failure");
        return {
          ...cached,
          success: true,
          fromCache: true,
          cacheError: error.message,
        };
      }

      return {
        workItems: [],
        workItemLinks: [],
        orgChartData: [],
        csvValidationData: { totalItems: 0, byType: {} },
        lastModified: null,
        success: false,
        error: error.message,
      };
    }
  }

  // Format last-modified timestamp for display with 3 timezones
  // Returns object with datePart and timezonesPart for two-line header display
  function formatRefreshTimestamp(isoString) {
    if (!isoString) return { datePart: "Unknown", timezonesPart: "" };
    try {
      const date = new Date(isoString);
      if (isNaN(date.getTime()))
        return { datePart: "Unknown", timezonesPart: "" };

      // Format date part
      const datePart = date.toLocaleDateString("en-US", {
        month: "numeric",
        day: "numeric",
        year: "numeric",
      });

      // Format time in 3 timezones
      const formatTime = (tz) =>
        date.toLocaleTimeString("en-US", {
          timeZone: tz,
          hour: "2-digit",
          minute: "2-digit",
          hour12: false,
        });

      const athensTime = formatTime("Europe/Athens");
      const bostonTime = formatTime("America/New_York");
      const seattleTime = formatTime("America/Los_Angeles");

      return {
        datePart: datePart,
        timezonesPart: `Athens ${athensTime} · Boston ${bostonTime} · Seattle ${seattleTime}`,
      };
    } catch (e) {
      return { datePart: "Unknown", timezonesPart: "" };
    }
  }

  // Clear cached data
  function clearCachedData() {
    try {
      cachedData = null;
      localStorage.removeItem(CACHE_KEY);
      console.log("Cache cleared");
    } catch (e) {
      console.warn("Failed to clear cache:", e.message);
    }
  }

  // Load Cascading Lists configuration (version ↔ date mappings)
  // Returns: { version, cascades, __etag, lastModified }
  async function loadCascadingLists() {
    const fileName = "cascading_lists.json";

    try {
      let result;

      if (isLocalhost) {
        // Local development - fetch from local file
        console.log("Loading cascading lists from local file...");
        const response = await fetch("./" + fileName, { cache: "no-store" });
        if (!response.ok) {
          throw new Error(`Failed to load ${fileName}: ${response.status}`);
        }
        const data = await response.json();
        result = { data, lastModified: null };
      } else {
        // Production: ADO is primary source of truth, SharePoint is fallback
        const account = msalInstance.getActiveAccount();
        if (!account) {
          await signIn();
        }

        try {
          console.log("Loading cascading lists from ADO (primary)...");
          const adoResult = await fetchCascadingListsFromADO();
          result = { data: adoResult.data, lastModified: null, __etag: adoResult.__etag };
        } catch (adoError) {
          console.warn("ADO fetch failed, falling back to SharePoint:", adoError.message);
          console.log("Loading cascading lists from SharePoint (fallback)...");
          result = await getSharePointFileById(
            CONFIG.SHAREPOINT.FILES.CASCADING_LISTS,
            fileName
          );
        }
      }

      return {
        version: result.data.version || "1.0",
        cascades: result.data.cascades || {},
        __etag: result.data.__etag || result.__etag || null,
        lastModified: result.lastModified,
        success: true,
      };
    } catch (error) {
      console.error("Failed to load cascading lists:", error);
      return {
        version: null,
        cascades: {},
        __etag: null,
        lastModified: null,
        success: false,
        error: error.message,
      };
    }
  }

  // Fetch cascading lists document directly from ADO Extension Management API
  async function fetchCascadingListsFromADO() {
    const token = await getAdoAccessToken();
    if (!token) {
      throw new Error("No ADO access token — user must sign in");
    }

    const url =
      "https://extmgmt.dev.azure.com/ncryptedcloud/_apis/ExtensionManagement/" +
      "InstalledExtensions/ms-devlabs/cascading-picklists-extension/Data/Scopes/" +
      "Default/Current/Collections/$settings/Documents/" +
      "manifest|7549e9c5-2259-4a1e-914b-e5989aeb4e3c" +
      "?api-version=7.1-preview.1";

    console.log("Fetching cascading lists from ADO Extension Management API...");
    const response = await fetch(url, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(
        `Failed to fetch cascading lists from ADO: ${response.status} ${response.statusText}\n${errorText}`
      );
    }

    const data = await response.json();
    // ADO wraps the document in { id, value: { version, cascades }, __etag }
    return {
      data: data.value || data,
      __etag: data.__etag || null,
      success: true,
    };
  }

  // Save cascading lists document to ADO Extension Management API (with __etag concurrency)
  async function saveCascadingListsToADO(updatedData, etag) {
    const token = await getAdoAccessToken();
    if (!token) {
      throw new Error("No ADO access token — user must sign in");
    }

    const docId = "manifest|7549e9c5-2259-4a1e-914b-e5989aeb4e3c";
    const url =
      "https://extmgmt.dev.azure.com/ncryptedcloud/_apis/ExtensionManagement/" +
      "InstalledExtensions/ms-devlabs/cascading-picklists-extension/Data/Scopes/" +
      "Default/Current/Collections/$settings/Documents/" +
      docId +
      "?api-version=7.1-preview.1";

    // ADO Extension Management expects { id, __etag, value: { version, cascades } }
    const payload = {
      id: docId,
      value: updatedData,
    };
    if (etag) {
      payload.__etag = etag;
    }

    console.log("Saving cascading lists to ADO Extension Management API...");
    const response = await fetch(url, {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (response.status === 409) {
      throw new Error(
        "CONFLICT: The cascading lists were modified by someone else. Please refresh and try again."
      );
    }

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(
        `Failed to save cascading lists to ADO: ${response.status} ${response.statusText}\n${errorText}`
      );
    }

    const data = await response.json();
    return {
      data: data.value || data,
      __etag: data.__etag || null,
      success: true,
    };
  }

  // Save cascading lists JSON to SharePoint file
  async function saveCascadingListsToSharePoint(updatedData) {
    if (isLocalhost || !msalInstance) {
      throw new Error("SharePoint write not available on localhost");
    }

    const accessToken = await getAccessToken();
    const fileId = CONFIG.SHAREPOINT.FILES.CASCADING_LISTS;

    const url = `https://graph.microsoft.com/v1.0/sites/${CONFIG.SHAREPOINT.SITE_ID}/drive/items/${fileId}/content`;

    console.log("Saving cascading lists to SharePoint...");
    const response = await fetch(url, {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(updatedData, null, 2),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(
        `Failed to save cascading lists to SharePoint: ${response.status} ${response.statusText}\n${errorText}`
      );
    }

    const data = await response.json();
    return { success: true, lastModified: data.lastModifiedDateTime };
  }

  // Save mention cache JSON to SharePoint for offline localhost dev (v215)
  async function saveMentionCacheToSharePoint(cacheData) {
    if (isLocalhost || !msalInstance) return;
    try {
      const accessToken = await getAccessToken();
      const url = `https://graph.microsoft.com/v1.0/sites/${CONFIG.SHAREPOINT.SITE_ID}/drive/root:/Product Planning/mention-cache.json:/content`;
      await fetch(url, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(cacheData, null, 2),
      });
    } catch (e) {
      console.warn('Failed to save mention cache to SharePoint:', e.message);
    }
  }

  // Fetch work item comments/discussion from ADO
  async function fetchWorkItemComments(workItemId) {
    const token = await getAdoAccessToken();
    if (!token) {
      // Localhost dev mode: return empty comments so UI is visible
      if (isLocalhost) return { success: true, comments: [], _localhost: true };
      return { success: false, error: 'Not authenticated' };
    }

    const url = `https://dev.azure.com/ncryptedcloud/eShare/_apis/wit/workItems/${workItemId}/comments?api-version=7.1-preview.4&$top=200&order=asc`;
    const response = await fetch(url, {
      headers: { 'Authorization': `Bearer ${token}` }
    });

    if (!response.ok) {
      return { success: false, error: `API returned ${response.status}` };
    }

    const data = await response.json();
    return { success: true, comments: data.comments || [] };
  }

  async function fetchWorkItemDescription(workItemId) {
    const token = await getAdoAccessToken();
    if (!token) {
      // Localhost dev mode: return empty description so UI is visible
      if (isLocalhost) return { success: true, description: '', _localhost: true };
      return { success: false, error: 'Not authenticated' };
    }

    const url = `https://dev.azure.com/ncryptedcloud/eShare/_apis/wit/workItems/${workItemId}?$select=System.Description&api-version=7.1`;
    const response = await fetch(url, {
      headers: { 'Authorization': `Bearer ${token}` }
    });

    if (!response.ok) {
      return { success: false, error: `API returned ${response.status}` };
    }

    const data = await response.json();
    return { success: true, description: (data.fields && data.fields['System.Description']) || '' };
  }

  // Batch fetch descriptions for multiple work items (up to 200 per call)
  async function batchFetchDescriptions(workItemIds) {
    const token = await getAdoAccessToken();
    if (!token) {
      if (isLocalhost) return { success: true, descriptions: {} };
      return { success: false, error: 'Not authenticated' };
    }
    const descriptions = {};
    // ADO supports up to 200 IDs per request
    const batchSize = 200;
    for (let i = 0; i < workItemIds.length; i += batchSize) {
      const batch = workItemIds.slice(i, i + batchSize);
      const ids = batch.join(',');
      const url = `https://dev.azure.com/ncryptedcloud/eShare/_apis/wit/workitems?ids=${ids}&fields=System.Description&api-version=7.1`;
      try {
        const resp = await fetch(url, { headers: { 'Authorization': `Bearer ${token}` } });
        if (resp.ok) {
          const data = await resp.json();
          if (data.value) {
            data.value.forEach(wi => {
              descriptions[wi.id] = (wi.fields && wi.fields['System.Description']) || '';
            });
          }
        }
      } catch (e) { console.warn('Batch description fetch error:', e); }
    }
    return { success: true, descriptions };
  }

  // Batch fetch comment counts for multiple work items (up to 200 per call)
  // Returns { success, commentCounts: { id: count } }
  async function batchFetchCommentCounts(workItemIds) {
    const token = await getAdoAccessToken();
    if (!token) {
      if (isLocalhost) return { success: true, commentCounts: {} };
      return { success: false, error: 'Not authenticated' };
    }
    const commentCounts = {};
    const batchSize = 200;
    for (let i = 0; i < workItemIds.length; i += batchSize) {
      const batch = workItemIds.slice(i, i + batchSize);
      const ids = batch.join(',');
      const url = `https://dev.azure.com/ncryptedcloud/eShare/_apis/wit/workitems?ids=${ids}&fields=System.CommentCount&api-version=7.1`;
      try {
        const resp = await fetch(url, { headers: { 'Authorization': `Bearer ${token}` } });
        if (resp.ok) {
          const data = await resp.json();
          if (data.value) {
            data.value.forEach(wi => {
              commentCounts[wi.id] = (wi.fields && wi.fields['System.CommentCount']) || 0;
            });
          }
        }
      } catch (e) { console.warn('Batch comment count fetch error:', e); }
    }
    return { success: true, commentCounts };
  }

  // Update one or more fields on an ADO work item via PATCH
  async function updateWorkItemFields(workItemId, fieldPatches) {
    let token = await getAdoAccessToken();
    if (!token) return { success: false, error: 'Not authenticated' };
    const url = `https://dev.azure.com/ncryptedcloud/eShare/_apis/wit/workitems/${workItemId}?api-version=7.0`;
    const body = fieldPatches.map(f => ({ op: 'replace', path: `/fields/${f.field}`, value: f.value }));
    let resp = await fetch(url, {
      method: 'PATCH',
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json-patch+json' },
      body: JSON.stringify(body)
    });
    if (resp.status === 401) {
      token = await getAdoAccessToken();
      if (!token) return { success: false, error: 'Token refresh failed' };
      resp = await fetch(url, {
        method: 'PATCH',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json-patch+json' },
        body: JSON.stringify(body)
      });
    }
    if (!resp.ok) {
      const errText = await resp.text();
      return { success: false, error: `${resp.status} ${resp.statusText}: ${errText}` };
    }
    return { success: true };
  }

  // ==================== WORK ITEM LINK MANAGEMENT ====================

  const ADO_LINK_TYPES = {
    'Parent': 'System.LinkTypes.Hierarchy-Reverse',
    'Child': 'System.LinkTypes.Hierarchy-Forward',
    'Related': 'System.LinkTypes.Related'
  };

  // Get work item with relations expanded (needed to find relation indices for removal)
  async function getWorkItemRelations(workItemId) {
    let token = await getAdoAccessToken();
    if (!token) return { success: false, error: 'Not authenticated' };
    const url = `https://dev.azure.com/ncryptedcloud/eShare/_apis/wit/workitems/${workItemId}?$expand=relations&api-version=7.0`;
    let resp = await fetch(url, {
      method: 'GET',
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (resp.status === 401) {
      token = await getAdoAccessToken();
      if (!token) return { success: false, error: 'Token refresh failed' };
      resp = await fetch(url, {
        method: 'GET',
        headers: { 'Authorization': `Bearer ${token}` }
      });
    }
    if (!resp.ok) {
      const errText = await resp.text();
      return { success: false, error: `${resp.status} ${resp.statusText}: ${errText}` };
    }
    const data = await resp.json();
    return { success: true, relations: data.relations || [] };
  }

  // Change a work item link from one type to another
  // sourceId: the work item we're modifying (source of the relationship)
  // targetId: the related work item
  // oldType: current relationship type ('Parent', 'Child', 'Related')
  // newType: desired relationship type ('Parent', 'Child', 'Related')
  async function changeWorkItemLink(sourceId, targetId, oldType, newType) {
    // Step 1: Get current relations to find the index of the old link
    const relResult = await getWorkItemRelations(sourceId);
    if (!relResult.success) return relResult;

    const relations = relResult.relations;
    const oldAdoRef = ADO_LINK_TYPES[oldType];
    const newAdoRef = ADO_LINK_TYPES[newType];
    if (!oldAdoRef || !newAdoRef) return { success: false, error: `Unknown link type: ${oldType} or ${newType}` };

    // Find the relation index matching the old link type and target work item
    const targetUrl = `https://dev.azure.com/ncryptedcloud/eShare/_apis/wit/workItems/${targetId}`;
    let removeIndex = -1;
    for (let i = 0; i < relations.length; i++) {
      const rel = relations[i];
      if (rel.rel === oldAdoRef && rel.url && rel.url.endsWith(`/${targetId}`)) {
        removeIndex = i;
        break;
      }
    }

    if (removeIndex === -1) {
      return { success: false, error: `Could not find existing ${oldType} link from ${sourceId} to ${targetId}` };
    }

    // Step 2: Build JSON Patch to remove old link and add new link
    // Important: remove first (index won't shift for the add since add uses /-), 
    // but we do remove first so that the index is valid
    const patchBody = [
      { op: 'remove', path: `/relations/${removeIndex}` },
      { op: 'add', path: '/relations/-', value: { rel: newAdoRef, url: targetUrl } }
    ];

    let token = await getAdoAccessToken();
    if (!token) return { success: false, error: 'Not authenticated' };
    const url = `https://dev.azure.com/ncryptedcloud/eShare/_apis/wit/workitems/${sourceId}?api-version=7.0`;
    let resp = await fetch(url, {
      method: 'PATCH',
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json-patch+json' },
      body: JSON.stringify(patchBody)
    });
    if (resp.status === 401) {
      token = await getAdoAccessToken();
      if (!token) return { success: false, error: 'Token refresh failed' };
      resp = await fetch(url, {
        method: 'PATCH',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json-patch+json' },
        body: JSON.stringify(patchBody)
      });
    }
    if (!resp.ok) {
      const errText = await resp.text();
      return { success: false, error: `${resp.status} ${resp.statusText}: ${errText}` };
    }
    return { success: true };
  }

  // Add a new link between two work items
  async function addWorkItemLink(sourceId, targetId, linkType) {
    const adoRef = ADO_LINK_TYPES[linkType];
    if (!adoRef) return { success: false, error: `Unknown link type: ${linkType}` };

    if (isLocalhost) return { success: false, error: 'Localhost: save disabled. Deploy to SharePoint to save links.' };

    const targetUrl = `https://dev.azure.com/ncryptedcloud/eShare/_apis/wit/workItems/${targetId}`;
    const patchBody = [
      { op: 'add', path: '/relations/-', value: { rel: adoRef, url: targetUrl } }
    ];

    let token = await getAdoAccessToken();
    if (!token) return { success: false, error: 'Not authenticated' };
    const url = `https://dev.azure.com/ncryptedcloud/eShare/_apis/wit/workitems/${sourceId}?api-version=7.0`;
    let resp = await fetch(url, {
      method: 'PATCH',
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json-patch+json' },
      body: JSON.stringify(patchBody)
    });
    if (resp.status === 401) {
      token = await getAdoAccessToken();
      if (!token) return { success: false, error: 'Token refresh failed' };
      resp = await fetch(url, {
        method: 'PATCH',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json-patch+json' },
        body: JSON.stringify(patchBody)
      });
    }
    if (!resp.ok) {
      const errText = await resp.text();
      return { success: false, error: `${resp.status} ${resp.statusText}: ${errText}` };
    }
    return { success: true };
  }

  // Add a comment to an ADO work item
  async function addWorkItemComment(workItemId, htmlText) {
    let token = await getAdoAccessToken();
    if (!token) {
      if (isLocalhost) return { success: false, error: 'Localhost: save disabled. Deploy to SharePoint to save comments.' };
      return { success: false, error: 'Not authenticated' };
    }
    const url = `https://dev.azure.com/ncryptedcloud/eShare/_apis/wit/workItems/${workItemId}/comments?api-version=7.1-preview.4`;
    let resp = await fetch(url, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: htmlText })
    });
    if (resp.status === 401) {
      token = await getAdoAccessToken();
      if (!token) return { success: false, error: 'Token refresh failed' };
      resp = await fetch(url, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: htmlText })
      });
    }
    if (!resp.ok) {
      const errText = await resp.text();
      return { success: false, error: `${resp.status} ${resp.statusText}: ${errText}` };
    }
    const data = await resp.json();
    return { success: true, comment: data };
  }

  // Update an existing comment on an ADO work item
  async function updateWorkItemComment(workItemId, commentId, htmlText) {
    let token = await getAdoAccessToken();
    if (!token) {
      if (isLocalhost) return { success: false, error: 'Localhost: save disabled. Deploy to SharePoint to save comments.' };
      return { success: false, error: 'Not authenticated' };
    }
    const url = `https://dev.azure.com/ncryptedcloud/eShare/_apis/wit/workItems/${workItemId}/comments/${commentId}?api-version=7.1-preview.4`;
    let resp = await fetch(url, {
      method: 'PATCH',
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: htmlText })
    });
    if (resp.status === 401) {
      token = await getAdoAccessToken();
      if (!token) return { success: false, error: 'Token refresh failed' };
      resp = await fetch(url, {
        method: 'PATCH',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: htmlText })
      });
    }
    if (!resp.ok) {
      const errText = await resp.text();
      return { success: false, error: `${resp.status} ${resp.statusText}: ${errText}` };
    }
    const data = await resp.json();
    return { success: true, comment: data };
  }

  // Update the description field on an ADO work item
  async function updateWorkItemDescription(workItemId, htmlText) {
    if (isLocalhost) return { success: false, error: 'Localhost: save disabled. Deploy to SharePoint to save descriptions.' };
    return updateWorkItemFields(workItemId, [
      { field: 'System.Description', value: htmlText }
    ]);
  }

  // Search ADO identities by display name (for @mention resolution)
  const _identityCache = {};
  async function searchAdoIdentities(searchText) {
    if (!searchText || searchText.length < 2) return [];
    const cacheKey = searchText.toLowerCase();
    if (_identityCache[cacheKey]) return _identityCache[cacheKey];
    let token = await getAdoAccessToken();
    if (!token) {
      // Localhost: return empty results (mentions will use fallback styling)
      return [];
    }
    const url = `https://vssps.dev.azure.com/ncryptedcloud/_apis/identities?searchFilter=General&filterValue=${encodeURIComponent(searchText)}&queryMembership=None&api-version=7.1`;
    try {
      let resp = await fetch(url, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (resp.status === 401) {
        token = await getAdoAccessToken();
        if (!token) return [];
        resp = await fetch(url, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
      }
      if (!resp.ok) return [];
      const data = await resp.json();
      const results = (data.value || [])
        .filter(id => id.isActive !== false && id.providerDisplayName)
        .map(id => ({
          id: id.id,
          displayName: id.providerDisplayName,
          uniqueName: id.properties?.Account?.$value || ''
        }));
      _identityCache[cacheKey] = results;
      return results;
    } catch (err) {
      console.warn('Identity search failed:', err);
      return [];
    }
  }

  // Get current signed-in user info
  function getCurrentUserInfo() {
    if (isLocalhost) {
      // Localhost dev mode: return mock user so editor UI is visible
      return { name: 'Dev User (localhost)', email: 'dev@localhost', _localhost: true };
    }
    if (!msalInstance) return null;
    const account = msalInstance.getActiveAccount();
    if (!account) return null;
    return {
      name: account.idTokenClaims?.name || account.username || 'Unknown',
      email: account.username || ''
    };
  }

  // ==================== PICKLIST MANAGEMENT ====================

  // Cache picklist IDs to avoid repeated lookups
  const _picklistIdCache = {};

  // Get the picklist ID for a custom field (e.g., 'Custom.CascadingVersion')
  async function fetchPicklistId(fieldRefName) {
    if (_picklistIdCache[fieldRefName]) return _picklistIdCache[fieldRefName];

    const token = await getAdoAccessToken();
    if (!token) throw new Error('No ADO access token');

    const url = `https://dev.azure.com/ncryptedcloud/eShare/_apis/wit/fields/${fieldRefName}?api-version=7.1`;
    const response = await fetch(url, {
      headers: { 'Authorization': `Bearer ${token}` }
    });

    if (!response.ok) {
      throw new Error(`Failed to get field metadata for ${fieldRefName}: ${response.status}`);
    }

    const field = await response.json();
    const picklistId = field.picklistId || field.picklist?.id;
    if (!picklistId) {
      throw new Error(`Field ${fieldRefName} does not have an associated picklist`);
    }

    _picklistIdCache[fieldRefName] = picklistId;
    return picklistId;
  }

  // Get current allowed values for a picklist
  async function fetchPicklistItems(picklistId) {
    const token = await getAdoAccessToken();
    if (!token) throw new Error('No ADO access token');

    const url = `https://dev.azure.com/ncryptedcloud/_apis/work/processes/lists/${picklistId}?api-version=7.1`;
    const response = await fetch(url, {
      headers: { 'Authorization': `Bearer ${token}` }
    });

    if (!response.ok) {
      throw new Error(`Failed to get picklist ${picklistId}: ${response.status}`);
    }

    const data = await response.json();
    return data;
  }

  // Update picklist with new items (PUT replaces the full list)
  async function updatePicklistItems(picklistId, picklistData) {
    const token = await getAdoAccessToken();
    if (!token) throw new Error('No ADO access token');

    const url = `https://dev.azure.com/ncryptedcloud/_apis/work/processes/lists/${picklistId}?api-version=7.1`;
    const response = await fetch(url, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(picklistData),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to update picklist ${picklistId}: ${response.status}\n${errorText}`);
    }

    return await response.json();
  }

  // Sync picklist allowed values with cascading list data
  // Ensures all version/date values in the cascade mapping exist as picklist options
  async function syncPicklistValues(cascadeData) {
    const cascades = cascadeData.cascades || {};
    const versionMap = cascades['Custom.CascadingVersion'] || {};
    const dateMap = cascades['Custom.CascadingDate'] || {};

    // Collect all unique version and date values from the cascade mapping
    const allVersions = new Set(Object.keys(versionMap));
    const allDates = new Set(Object.keys(dateMap));

    // Also collect values from reverse mappings
    for (const entry of Object.values(dateMap)) {
      const versions = entry['Custom.CascadingVersion'] || [];
      versions.forEach(v => allVersions.add(v));
    }
    for (const entry of Object.values(versionMap)) {
      const dates = entry['Custom.CascadingDate'] || [];
      dates.forEach(d => allDates.add(d));
    }

    const results = { versionsAdded: [], datesAdded: [], versionsRemoved: [], datesRemoved: [] };

    // Sync version picklist
    try {
      const versionPicklistId = await fetchPicklistId('Custom.CascadingVersion');
      const versionPicklist = await fetchPicklistItems(versionPicklistId);
      const existingVersions = new Set(versionPicklist.items || []);
      const newVersions = [...allVersions].filter(v => !existingVersions.has(v));
      const staleVersions = [...existingVersions].filter(v => !allVersions.has(v));

      if (newVersions.length > 0 || staleVersions.length > 0) {
        const mergedItems = [...allVersions].sort();
        await updatePicklistItems(versionPicklistId, {
          ...versionPicklist,
          items: mergedItems,
        });
        results.versionsAdded = newVersions;
        results.versionsRemoved = staleVersions;
        if (newVersions.length > 0) console.log(`Added ${newVersions.length} version(s) to picklist:`, newVersions);
        if (staleVersions.length > 0) console.log(`Removed ${staleVersions.length} version(s) from picklist:`, staleVersions);
      }
    } catch (err) {
      console.warn('Failed to sync version picklist:', err);
      throw new Error(`Version picklist sync failed: ${err.message}`);
    }

    // Sync date picklist
    try {
      const datePicklistId = await fetchPicklistId('Custom.CascadingDate');
      const datePicklist = await fetchPicklistItems(datePicklistId);
      const existingDates = new Set(datePicklist.items || []);
      const newDates = [...allDates].filter(d => !existingDates.has(d));
      const staleDates = [...existingDates].filter(d => !allDates.has(d));

      if (newDates.length > 0 || staleDates.length > 0) {
        const mergedItems = [...allDates].sort();
        await updatePicklistItems(datePicklistId, {
          ...datePicklist,
          items: mergedItems,
        });
        results.datesAdded = newDates;
        results.datesRemoved = staleDates;
        if (newDates.length > 0) console.log(`Added ${newDates.length} date(s) to picklist:`, newDates);
        if (staleDates.length > 0) console.log(`Removed ${staleDates.length} date(s) from picklist:`, staleDates);
      }
    } catch (err) {
      console.warn('Failed to sync date picklist:', err);
      throw new Error(`Date picklist sync failed: ${err.message}`);
    }

    return results;
  }

  // Export to global scope
  window.DashboardLoader = {
    loadDashboardData,
    loadCascadingLists,
    fetchCascadingListsFromADO,
    saveCascadingListsToADO,
    saveCascadingListsToSharePoint,
    saveMentionCacheToSharePoint,
    syncPicklistValues,
    fetchPicklistId,
    fetchPicklistItems,
    updatePicklistItems,
    fetchWorkItemComments,
    batchFetchDescriptions,
    batchFetchCommentCounts,
    fetchWorkItemDescription,
    updateWorkItemFields,
    getWorkItemRelations,
    changeWorkItemLink,
    addWorkItemLink,
    addWorkItemComment,
    updateWorkItemComment,
    updateWorkItemDescription,
    searchAdoIdentities,
    getCurrentUserInfo,
    formatRefreshTimestamp,
    CONFIG,
    transformWorkItem,
    transformWorkItemLink,
    extractTeamFromAreaPath,
    extractIterationFromPath,
    signOut,
    signIn,
    clearCachedData,
    loadCachedData,
    getAdoAccessToken,
  };
})(window);
