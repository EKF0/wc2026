export async function onRequestPost(context) {
  try {
    const { request, env } = context;
    const contentType = request.headers.get("content-type") || "";
    
    let email = "";
    let utm_source = "";
    let utm_medium = "";
    let utm_campaign = "";

    if (contentType.includes("form")) {
      const formData = await request.formData();
      email = formData.get("email");
      utm_source = formData.get("utm_source") || "";
      utm_medium = formData.get("utm_medium") || "";
      utm_campaign = formData.get("utm_campaign") || "";
    } else {
      const data = await request.json();
      email = data.email;
      utm_source = data.utm_source || "";
      utm_medium = data.utm_medium || "";
      utm_campaign = data.utm_campaign || "";
    }

    if (!email || !email.includes("@")) {
      return new Response(JSON.stringify({ error: "Invalid email address" }), {
        status: 400,
        headers: { 
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*"
        }
      });
    }

    // Check if D1 database exists
    if (!env.DB) {
      console.warn("DB binding not found. Falling back to log.");
      return new Response(JSON.stringify({ 
        success: true, 
        message: "Successfully subscribed (Development fallback: DB binding missing)" 
      }), {
        status: 200,
        headers: { 
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*"
        }
      });
    }

    // Insert subscriber into D1 database
    await env.DB.prepare(
      "INSERT OR IGNORE INTO subscribers (email, utm_source, utm_medium, utm_campaign) VALUES (?, ?, ?, ?)"
    ).bind(email, utm_source, utm_medium, utm_campaign).run();

    return new Response(JSON.stringify({ success: true, message: "Successfully subscribed!" }), {
      status: 200,
      headers: { 
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
      }
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), {
      status: 500,
      headers: { 
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
      }
    });
  }
}

// Support preflight OPTIONS request for CORS
export async function onRequestOptions(context) {
  return new Response(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
      "Access-Control-Max-Age": "86400"
    }
  });
}
