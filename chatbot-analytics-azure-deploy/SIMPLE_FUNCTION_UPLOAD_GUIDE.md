# 🚀 Simple Function Loading Guide (Portal Only)

**After clicking "Deploy to Azure", follow these 3 easy steps to load your functions:**

## Step 1: Open Your Function App
1. Go to [Azure Portal](https://portal.azure.com)
2. Click **Resource Groups** in the left menu
3. Click your resource group (usually starts with `rg-`)
4. Click your **Function App** (starts with `func-`)

## Step 2: Upload Functions
1. In your Function App, click **Functions** in the left menu
2. Click **+ Create** button at the top
3. Choose **Upload a .zip file**
4. **Download link**: [function-app-corrected.zip](https://github.com/Russ-Holloway/CoPPA-Analytics/raw/main/chatbot-analytics-azure-deploy/function-app-corrected.zip)
5. Right-click → Save the ZIP file to your computer
6. Click **Browse** and select the downloaded ZIP file
7. Click **Upload**

## Step 3: Verify Functions Loaded
1. Wait 2-3 minutes for upload to complete
2. Click **Functions** in the left menu again
3. You should see 7 functions:
   - ✅ **GetAnalytics** (main analytics API)
   - ✅ **Dashboard** (web interface)
   - ✅ **GetQuestions** (question data)
   - ✅ **SeedData** (demo data)
   - ✅ **TestFunction** (health check)
   - ✅ **TimerTrigger** (scheduled tasks)
   - ✅ **FunctionSync** (status helper)

## 🎉 Test Your Analytics
- Click **GetAnalytics** function
- Click **Code + Test** tab
- Click **Test/Run** button
- Click **Run** (leave default settings)
- You should see analytics data!

## 📊 Access Your Dashboard
Your dashboard URL: `https://[your-function-app-name].azurewebsites.net/api/Dashboard`

---

**⚠️ If upload fails:** Your Function App might be on Windows instead of Linux. Contact your IT team to recreate it on a Linux plan.

**💡 Need help?** The functions are already built and ready - this is just uploading them to your Function App.
