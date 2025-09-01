# 🚀 Vercel Deployment - Simple Hindi Guide

## Step 1: Code ko GitHub pe push karo

```bash
# Terminal mein ye commands run karo:
git add .
git commit -m "Ready for Vercel deployment"
git push origin main
```

## Step 2: Vercel Account banao

1. [vercel.com](https://vercel.com) pe jao
2. "Sign up with GitHub" click karo
3. GitHub se login karo

## Step 3: Project Deploy karo

1. Vercel dashboard mein "New Project" click karo
2. Apna `Retail-Analytics-Platform` repository select karo
3. **IMPORTANT**: Ye settings lagao:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend` (ye important hai!)
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

## Step 4: Environment Variables lagao

Vercel mein ye environment variables add karo:

```
SECRET_KEY=myawesomesecretkey123
OPENAI_API_KEY=your-openai-key-here
DATABASE_URL=sqlite:///./retail_analytics.db
ENVIRONMENT=production
DEBUG=false
```

## Step 5: Deploy karo!

1. "Deploy" button click karo
2. 2-3 minutes wait karo
3. Ho gaya! 🎉

## Aapka App Ready!

- Frontend: `https://your-app-name.vercel.app`
- API: `https://your-app-name.vercel.app/api`
- Docs: `https://your-app-name.vercel.app/docs`

## Agar Error Aaye To:

1. Build logs check karo
2. Environment variables sahi hai ya nahi check karo
3. GitHub code latest hai ya nahi check karo

## Important Notes:

- **Root Directory**: Frontend folder select karna zaroori hai
- **API**: Automatically `/api` route pe available hoga
- **Database**: SQLite use kar rahe hain (temporary)
- **Free Tier**: Vercel free mein deploy ho jayega

## Baad Mein Upgrade:

- PostgreSQL database add kar sakte hain
- Custom domain add kar sakte hain
- More features enable kar sakte hain

---

**Mushkil hai koi baat? Message karo! 💬**
