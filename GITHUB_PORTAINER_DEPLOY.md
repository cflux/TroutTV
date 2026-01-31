# Deploying TroutTV from GitHub to Portainer

This guide explains how to deploy TroutTV directly from your GitHub repository to Portainer.

## Prerequisites

- GitHub repository with TroutTV code
- Portainer installed and accessible
- Docker host with internet access

## The Image Problem

Portainer **cannot build Docker images** from repositories. You must provide a pre-built image. You have three options:

---

## Method 1: Build Locally First (Quickest)

Best if you only have one Docker host.

### Step 1: Clone and Build on Docker Host

SSH into your Docker host and run:

```bash
# Clone your repository
git clone https://github.com/yourusername/TroutTV.git
cd TroutTV

# Build the image
docker build -t trouttv:latest .

# Verify
docker images | grep trouttv
```

### Step 2: Deploy Stack from GitHub in Portainer

1. **Login to Portainer**
2. **Stacks → Add stack**
3. **Name:** `trouttv`
4. **Build method:** Select **"Repository"**
5. **Repository configuration:**
   - **Repository URL:** `https://github.com/yourusername/TroutTV`
   - **Repository reference:** `main` (or your branch)
   - **Compose path:** `docker-compose.yml`
6. **Environment variables:** Click "Add environment variable" and add:
   - Name: `BASE_URL`
   - Value: `http://YOUR_SERVER_IP:8000`
7. **Deploy the stack**

The stack will use the locally built `trouttv:latest` image.

### Updating

To update:
```bash
cd TroutTV
git pull
docker build -t trouttv:latest .
```

Then in Portainer: Stacks → trouttv → Update the stack → Re-pull image and redeploy

---

## Method 2: Use Docker Hub (Recommended for Multiple Hosts)

Best if you want to deploy to multiple servers or share the image.

### Step 1: Push Image to Docker Hub

On your development machine:

```bash
# Login to Docker Hub
docker login

# Build and tag for Docker Hub
docker build -t yourusername/trouttv:latest .

# Push to Docker Hub
docker push yourusername/trouttv:latest
```

### Step 2: Update docker-compose.yml in GitHub

Edit the `docker-compose.yml` file in your repository and change the image line:

```yaml
services:
  trouttv:
    image: yourusername/trouttv:latest  # Change yourusername!
```

Commit and push:
```bash
git add docker-compose.yml
git commit -m "Use Docker Hub image"
git push
```

### Step 3: Deploy from GitHub in Portainer

1. **Stacks → Add stack**
2. **Build method:** "Repository"
3. **Repository URL:** `https://github.com/yourusername/TroutTV`
4. **Repository reference:** `main`
5. **Add environment variable:**
   - `BASE_URL` = `http://YOUR_SERVER_IP:8000`
6. **Deploy**

Portainer will automatically pull the image from Docker Hub!

### Updating

```bash
# Build new version
docker build -t yourusername/trouttv:latest .

# Push to Docker Hub
docker push yourusername/trouttv:latest
```

In Portainer: Update stack → Re-pull image and redeploy

---

## Method 3: Use GitHub Container Registry (GHCR)

Best if you want to keep everything in GitHub's ecosystem.

### Step 1: Create GitHub Personal Access Token

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token
3. Scopes: Select `write:packages` and `read:packages`
4. Copy the token (save it securely!)

### Step 2: Login and Push to GHCR

```bash
# Login to GitHub Container Registry
echo YOUR_GITHUB_TOKEN | docker login ghcr.io -u yourusername --password-stdin

# Build and tag for GHCR
docker build -t ghcr.io/yourusername/trouttv:latest .

# Push to GHCR
docker push ghcr.io/yourusername/trouttv:latest
```

### Step 3: Make Package Public (or configure authentication)

**Option A: Make Public (Easier)**
1. Go to https://github.com/yourusername?tab=packages
2. Click on `trouttv` package
3. Package settings → Change visibility → Public

**Option B: Use Authentication in Portainer**
- In Portainer stack deployment, add registry authentication
- Use your GitHub username and personal access token

### Step 4: Update docker-compose.yml

```yaml
services:
  trouttv:
    image: ghcr.io/yourusername/trouttv:latest
```

Commit and push to GitHub.

### Step 5: Deploy in Portainer

Same as Method 2, but the image comes from GHCR instead of Docker Hub.

---

## Method 4: Web Editor (No GitHub Pull)

If you don't want to pull from GitHub at all:

1. **Copy** the contents of `portainer-stack.yml` from your GitHub repo
2. In Portainer: **Stacks → Add stack**
3. **Build method:** "Web editor"
4. **Paste** the stack content
5. **Modify** the image line to point to your registry:
   ```yaml
   image: yourusername/trouttv:latest
   ```
6. **Update** BASE_URL and media path
7. **Deploy**

---

## Comparison

| Method | Pros | Cons | Best For |
|--------|------|------|----------|
| **Local Build** | Quick, no registry needed | Manual build on each host | Single server |
| **Docker Hub** | Easy sharing, auto-pull | Public or paid account | Multiple servers |
| **GHCR** | Integrated with GitHub | Requires token setup | GitHub-centric workflow |
| **Web Editor** | Simple, no repo needed | No version control | Testing/quick deploy |

---

## Recommended: Docker Hub Workflow

For most users, I recommend **Method 2 (Docker Hub)**:

1. **One-time setup:**
   ```bash
   docker build -t yourusername/trouttv:latest .
   docker push yourusername/trouttv:latest
   ```

2. **Update docker-compose.yml in GitHub:**
   ```yaml
   image: yourusername/trouttv:latest
   ```

3. **Deploy in Portainer:**
   - Repository URL: Your GitHub repo
   - Environment variable: BASE_URL
   - Done!

4. **To update:**
   - Rebuild and push image
   - In Portainer: Update stack with re-pull

---

## Environment Variables in Portainer Repository Mode

When deploying from a repository, add these environment variables in the Portainer UI:

### Required
```
BASE_URL=http://192.168.1.100:8000
```

### Optional (if you want to override defaults)
```
STREAM_TIMEOUT=60
CLEANUP_INTERVAL=30
EPG_DAYS_AHEAD=2
```

**Important:** Don't put sensitive data in the docker-compose.yml file if your repo is public! Use Portainer's environment variables instead.

---

## Troubleshooting

### "Image not found" error

**Problem:** Portainer can't find `trouttv:latest`

**Solutions:**
- Method 1: Build image locally first
- Method 2/3: Push to registry and update `docker-compose.yml`
- Check image name matches exactly in `docker-compose.yml`

### "Failed to pull repository"

**Problem:** Portainer can't access GitHub

**Solutions:**
- Check repository is public OR configure credentials
- Check URL is correct (no `.git` needed)
- Try: `https://github.com/username/repo` not `git@github...`

### "Cannot pull private image"

**Problem:** Image is in private registry

**Solutions:**
- Make package public (GHCR or Docker Hub)
- Or configure registry authentication in Portainer:
  - Registries → Add registry
  - Type: DockerHub or Custom (for GHCR)
  - Credentials: Your username and token

### Stack deploys but container won't start

**Problem:** Configuration issues

**Solutions:**
- Check Portainer logs: Containers → trouttv → Logs
- Verify BASE_URL is set correctly
- Verify media volume path exists on host
- Check port 8000 isn't already in use

---

## Complete Example: Docker Hub Deployment

Here's a complete workflow:

```bash
# On your development machine
git clone https://github.com/yourusername/TroutTV.git
cd TroutTV

# Build image
docker build -t yourusername/trouttv:latest .

# Push to Docker Hub
docker login
docker push yourusername/trouttv:latest

# Update the repo
# Edit docker-compose.yml, change: image: yourusername/trouttv:latest
git add docker-compose.yml
git commit -m "Use Docker Hub image"
git push
```

**In Portainer:**
1. Stacks → Add stack
2. Name: `trouttv`
3. Build method: Repository
4. Repository URL: `https://github.com/yourusername/TroutTV`
5. Reference: `main`
6. Compose path: `docker-compose.yml`
7. Environment variables:
   - `BASE_URL` = `http://192.168.1.100:8000`
8. Deploy the stack

**Done!** Stack pulls from GitHub, image pulls from Docker Hub, everything is version controlled.

---

## Need Help?

- Can't build image? See: `QUICKSTART.md`
- Can't deploy in Portainer? See: `PORTAINER_DEPLOY.md`
- General issues? See: `README.md`

Choose the method that best fits your workflow and infrastructure!
