function normalizeLeadPayload(payload) {
  const safe = payload || {};
  return {
    timestamp: String(safe.timestamp || safe.received_at || new Date().toISOString()),
    name: String(safe.name || ""),
    email: String(safe.email || ""),
    phone: String(safe.phone || ""),
    message: String(safe.message || safe.body_preview || ""),
    source: String(safe.source || ""),
    intent: String(safe.intent || ""),
    priority: String(safe.priority || ""),
  };
}

function hasLeadData(payload) {
  return [
    payload.name,
    payload.email,
    payload.phone,
    payload.message,
    payload.source,
    payload.intent,
    payload.priority,
  ].some((value) => String(value || "").trim());
}

function appendLeadRow(payload) {
  const normalized = normalizeLeadPayload(payload);
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];
  sheet.appendRow([
    normalized.timestamp,
    normalized.name,
    normalized.email,
    normalized.phone,
    normalized.message,
    normalized.source,
    normalized.intent,
    normalized.priority,
  ]);
  return normalized;
}

function jsonResponse(body, statusCode) {
  return ContentService
    .createTextOutput(JSON.stringify({
      ok: statusCode < 400,
      statusCode: statusCode,
      ...body,
    }))
    .setMimeType(ContentService.MimeType.JSON);
}

function handlePayload(payload, method) {
  try {
    const normalized = normalizeLeadPayload(payload);
    if (!hasLeadData(normalized)) {
      return jsonResponse({
        message: "Empty payload ignored",
        method: method,
        received: normalized,
      }, 400);
    }
    appendLeadRow(normalized);
    return jsonResponse({
      message: "Lead logged",
      method: method,
      received: normalized,
    }, 200);
  } catch (error) {
    return jsonResponse({ message: String(error), method: method }, 500);
  }
}

function doGet(e) {
  return handlePayload((e && e.parameter) || {}, "GET");
}

function doPost(e) {
  let payload = (e && e.parameter) || {};

  if (e && e.postData && e.postData.contents) {
    try {
      payload = {
        ...payload,
        ...JSON.parse(e.postData.contents),
      };
    } catch (error) {
      payload = {
        ...payload,
        raw_body: e.postData.contents,
      };
    }
  }

  return handlePayload(payload, "POST");
}
