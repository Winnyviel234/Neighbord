// Edge Function de referencia para Supabase.
// Despliegue:
// supabase functions deploy send-email
// supabase secrets set RESEND_API_KEY=...

type EmailPayload = {
  to: string[];
  subject: string;
  html: string;
};

Deno.serve(async (req) => {
  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "Metodo no permitido" }), { status: 405 });
  }

  const apiKey = Deno.env.get("RESEND_API_KEY");
  if (!apiKey) {
    return new Response(JSON.stringify({ error: "RESEND_API_KEY no configurada" }), { status: 500 });
  }

  const payload = (await req.json()) as EmailPayload;
  const response = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${apiKey}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      from: "Neighbord <notificaciones@tu-dominio.com>",
      to: payload.to,
      subject: payload.subject,
      html: payload.html
    })
  });

  const data = await response.json();
  return new Response(JSON.stringify(data), {
    status: response.status,
    headers: { "Content-Type": "application/json" }
  });
});
