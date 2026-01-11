# OAuth Setup Guide for OpenAlex Dashboard

This guide explains how to enable Google and GitHub OAuth authentication in Supabase for the OpenAlex Dashboard.

## 1. Google OAuth Setup

### Step 1: Create Google OAuth Credentials

1. Go to [Google Cloud Console - Credentials](https://console.cloud.google.com/apis/credentials)
2. Click **Create Credentials** → **OAuth 2.0 Client ID**
3. Select **Web application** as the application type
4. Configure the following:
   - **Name**: OpenAlex Dashboard (or your preferred name)
   - **Authorized redirect URIs**: Add the following URI:
     ```
     https://msnxwmvuwdvfwdeukgxt.supabase.co/auth/v1/callback
     ```
5. Click **Create**
6. Copy the **Client ID** and **Client Secret**

### Step 2: Configure Supabase

1. Go to your [Supabase Dashboard](https://supabase.com/dashboard)
2. Navigate to **Authentication** → **Providers** → **Google**
3. Toggle **Enable Google provider** to ON
4. Paste the **Client ID** and **Client Secret** from Google
5. Click **Save**

---

## 2. GitHub OAuth Setup

### Step 1: Create GitHub OAuth App

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click **New OAuth App**
3. Fill in the following details:
   - **Application name**: OpenAlex Dashboard (or your preferred name)
   - **Homepage URL**:
     ```
     https://openalex-dashboard-l2yut6xcta-uc.a.run.app
     ```
   - **Authorization callback URL**:
     ```
     https://msnxwmvuwdvfwdeukgxt.supabase.co/auth/v1/callback
     ```
4. Click **Register application**
5. Copy the **Client ID**
6. Click **Generate a new client secret** and copy the **Client Secret**

### Step 2: Configure Supabase

1. Go to your [Supabase Dashboard](https://supabase.com/dashboard)
2. Navigate to **Authentication** → **Providers** → **GitHub**
3. Toggle **Enable GitHub provider** to ON
4. Paste the **Client ID** and **Client Secret** from GitHub
5. Click **Save**

---

## 3. Testing

After enabling the OAuth providers:

1. Restart your application to ensure the configuration is loaded
2. Navigate to the login page
3. The **Google** and **GitHub** login buttons should now be functional
4. Click each button to verify the OAuth flow redirects correctly and authenticates users

### Troubleshooting

- **Redirect URI mismatch**: Ensure the callback URL in your OAuth provider settings exactly matches `https://msnxwmvuwdvfwdeukgxt.supabase.co/auth/v1/callback`
- **Invalid credentials**: Double-check that the Client ID and Client Secret are copied correctly without extra spaces
- **Provider not enabled**: Verify the provider toggle is ON in Supabase Authentication settings
