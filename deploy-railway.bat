@echo off
echo Setting up Railway environment variables...

railway variables add APP_NAME=task_web_app
railway variables add ENVIRONMENT=production
railway variables add DEBUG=False
railway variables add DATABASE_URL=sqlite:///./email_categorizer.db
railway variables add SECRET_KEY=WOssrngcVXWDKhUXk8hmcJZZbC3MbNb9vNLwdocywrI
railway variables add ALGORITHM=HS256
railway variables add ACCESS_TOKEN_EXPIRE_MINUTES=30
railway variables add JWT_SECRET_KEY=your_super_secret_jwt_key_here_make_it_very_long_and_random
railway variables add JWT_ALGORITHM=HS256
railway variables add JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
railway variables add GOOGLE_OAUTH_CLIENT_ID=11961450926-agk41r98cgdob9qt1kc916k8qdf7t31d.apps.googleusercontent.com
railway variables add GOOGLE_OAUTH_CLIENT_SECRET=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
railway variables add GOOGLE_OAUTH_REDIRECT_URI=https://your-railway-url.up.railway.app/auth/gmail/callback
railway variables add RESEND_API_KEY=re_PXTZkYmk_JqKiQGZEkHVjHkUBdpaWjtvf
railway variables add CORS_ORIGINS=http://localhost:3000,https://your-vercel-url.vercel.app

echo Environment variables set successfully!
echo Now run: railway up --detach