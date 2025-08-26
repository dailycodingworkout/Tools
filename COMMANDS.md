# Git Branch Migration Commands

Simple list of GitHub and Linux commands to migrate multiple branches from source repo to target repo.

## Setup Commands

```bash
# Clone source repository
git clone https://github.com/your-username/source-repo.git source
cd source

# Clone target repository  
git clone https://github.com/your-username/target-repo.git target
cd target
```

## Migration Commands (repeat for each branch)

```bash
# Go to source repo
cd source

# Switch to branch you want to migrate (e.g., 18.0)
git checkout 18.0

# Go to target repo
cd ../target

# Create folder for this version (e.g., v18)
mkdir -p v18

# Copy all files from source branch to target folder
cp -r ../source/* v18/ 2>/dev/null || true
cp -r ../source/.* v18/ 2>/dev/null || true

# Remove git folder from copied content
rm -rf v18/.git

# Add and commit changes
git add .
git commit -m "Add v18 from 18.0 branch"
```

## Repeat for All Branches

```bash
# For master branch
cd source && git checkout master
cd ../target && mkdir -p master
cp -r ../source/* master/ 2>/dev/null || true
cp -r ../source/.* master/ 2>/dev/null || true
rm -rf master/.git
git add . && git commit -m "Add master branch"

# For 17.0 branch  
cd source && git checkout 17.0
cd ../target && mkdir -p v17
cp -r ../source/* v17/ 2>/dev/null || true
cp -r ../source/.* v17/ 2>/dev/null || true
rm -rf v17/.git
git add . && git commit -m "Add v17 from 17.0 branch"

# For 16.0 branch
cd source && git checkout 16.0  
cd ../target && mkdir -p v16
cp -r ../source/* v16/ 2>/dev/null || true
cp -r ../source/.* v16/ 2>/dev/null || true
rm -rf v16/.git
git add . && git commit -m "Add v16 from 16.0 branch"

# For 15.0 branch
cd source && git checkout 15.0
cd ../target && mkdir -p v15  
cp -r ../source/* v15/ 2>/dev/null || true
cp -r ../source/.* v15/ 2>/dev/null || true
rm -rf v15/.git
git add . && git commit -m "Add v15 from 15.0 branch"
```

## Final Commands

```bash
# Push all changes to remote
cd target
git push origin main

# Clean up local repos (optional)
cd ..
rm -rf source target
```

## Result Structure

```
target-repo/
├── master/     # Files from master branch
├── v18/        # Files from 18.0 branch  
├── v17/        # Files from 17.0 branch
├── v16/        # Files from 16.0 branch
└── v15/        # Files from 15.0 branch
```