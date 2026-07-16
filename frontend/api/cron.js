export default async function handler(req, res) {
  try {
    const backendUrl = process.env.PUBLIC_API_URL || 'https://synapsehr-6qwi.onrender.com';
    const response = await fetch(`${backendUrl}/health`);
    const data = await response.json();
    res.status(200).json({ status: 'ok', render_status: data });
  } catch (error) {
    res.status(500).json({ status: 'error', message: error.message });
  }
}
