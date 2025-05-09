const express = require('express');
const axios = require('axios');
const dotenv = require('dotenv');
const cors = require('cors');

dotenv.config();
const app = express();
app.use(cors());
app.use(express.json());

async function getZohoAccessToken() {
  try {
    const res = await axios.post('https://accounts.zoho.eu/oauth/v2/token', null, {
      params: {
        refresh_token: process.env.ZOHO_REFRESH_TOKEN,
        client_id: process.env.ZOHO_CLIENT_ID,
        client_secret: process.env.ZOHO_CLIENT_SECRET,
        grant_type: 'refresh_token'
      }
    });
    return res.data.access_token;
  } catch (err) {
    console.error('Failed to fetch Zoho token:', err.response?.data || err.message);
    return null;
  }
}

app.post('/verify', async (req, res) => {
  const { email, token } = req.body;

  // ✅ Validate input
  if (!email || !token) {
    return res.status(400).json({ error: "Email and reCAPTCHA token required" });
  }

  // ✅ Verify reCAPTCHA token
  try {
    const verifyURL = 'https://www.google.com/recaptcha/api/siteverify';
    const verifyResponse = await axios.post(verifyURL, null, {
      params: {
        secret: process.env.RECAPTCHA_SECRET,
        response: token
      }
    });

    if (!verifyResponse.data.success) {
      return res.status(400).json({ error: "Failed reCAPTCHA verification" });
    }
  } catch (err) {
    console.error("reCAPTCHA verification error:", err.response?.data || err.message);
    return res.status(500).json({ error: "Error verifying reCAPTCHA" });
  }

  // ✅ Fetch Zoho Access Token
  const accessToken = await getZohoAccessToken();
  if (!accessToken) return res.status(500).json({ error: 'Failed to get Zoho token' });

  // ✅ Save to Zoho CRM
  try {
    const response = await axios.post(
      process.env.ZOHO_API_URL,
      {
        data: [
          {
            Email: email,
            Last_Name: 'FUN-BET Lead',
            Lead_Source: 'Early Signup'
          }
        ]
      },
      {
        headers: {
          Authorization: `Zoho-oauthtoken ${accessToken}`,
          'Content-Type': 'application/json'
        }
      }
    );

    console.log('Zoho Response:', response.data);
    res.json({ success: true });
    console.log(email)
  } catch (err) {
    console.error('Zoho Lead Error:', err.response?.data || err.message);
    res.status(500).json({ error: 'Failed to save lead to Zoho' });
  }
});

app.get('/', (req, res) => {
  res.send('✅ Backend is live');
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
