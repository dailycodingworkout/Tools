# Git Branch Migration Commands

Two approaches for migrating multiple branches from source repo to target repo:

## ⚠️ IMPORTANT: Choose Your Approach

### Option A: Simple File Copy (FAST - No History Preservation)
✅ **Pros**: Fast, simple commands, no git complexity  
❌ **Cons**: Loses all git history, commit messages, and author information

### Option B: History-Preserving Migration (COMPLEX - Full History Preservation) 
✅ **Pros**: Preserves complete git history, commits, authors, timestamps  
❌ **Cons**: More complex commands, takes longer

---

## Option A: Simple File Copy (No History)

⚠️ **WARNING**: This approach does NOT preserve git history. It only copies the current files from each branch.

### Setup Commands
```bash
# Clone source repository
git clone https://github.com/your-username/source-repo.git source
cd source

# Clone target repository  
git clone https://github.com/your-username/target-repo.git target
cd target
```

### Migration Commands (repeat for each branch)
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

# Remove git folder from copied content (THIS REMOVES ALL HISTORY)
rm -rf v18/.git

# Add and commit changes
git add .
git commit -m "Add v18 from 18.0 branch (files only, no history)"
```

### Repeat for All Branches
```bash
# For master branch
cd source && git checkout master
cd ../target && mkdir -p master
cp -r ../source/* master/ 2>/dev/null || true
cp -r ../source/.* master/ 2>/dev/null || true
rm -rf master/.git
git add . && git commit -m "Add master branch (files only, no history)"

# For 17.0 branch  
cd source && git checkout 17.0
cd ../target && mkdir -p v17
cp -r ../source/* v17/ 2>/dev/null || true
cp -r ../source/.* v17/ 2>/dev/null || true
rm -rf v17/.git
git add . && git commit -m "Add v17 from 17.0 branch (files only, no history)"

# For 16.0 branch
cd source && git checkout 16.0  
cd ../target && mkdir -p v16
cp -r ../source/* v16/ 2>/dev/null || true
cp -r ../source/.* v16/ 2>/dev/null || true
rm -rf v16/.git
git add . && git commit -m "Add v16 from 16.0 branch (files only, no history)"

# For 15.0 branch
cd source && git checkout 15.0
cd ../target && mkdir -p v15  
cp -r ../source/* v15/ 2>/dev/null || true
cp -r ../source/.* v15/ 2>/dev/null || true
rm -rf v15/.git
git add . && git commit -m "Add v15 from 15.0 branch (files only, no history)"
```

### Final Commands for Option A
```bash
# Push all changes to remote
cd target
git push origin main

# Clean up local repos (optional)
cd ..
rm -rf source target
```

---

## Option B: History-Preserving Migration (Full History)

✅ **This approach preserves complete git history, commits, and author information**

### Setup Commands
```bash
# Clone target repository first
git clone https://github.com/your-username/target-repo.git target
cd target

# Add source repository as a remote
git remote add source-repo https://github.com/your-username/source-repo.git

# Fetch all branches from source repository
git fetch source-repo
```

### Migration Commands (repeat for each branch)
```bash
# For 18.0 branch -> v18 folder
# Create a new branch from the source branch
git checkout -b migrate-18.0 source-repo/18.0

# Create target folder and move all files into it
mkdir -p v18-temp
find . -maxdepth 1 -not -name . -not -name .. -not -name ".git" -not -name "v18-temp" -exec mv {} v18-temp/ \;
mv v18-temp v18

# Commit the reorganization (preserving original commits)
git add .
git commit -m "Reorganize 18.0 branch content into v18 folder

Original branch: 18.0  
Migration timestamp: $(date -u)
This commit preserves the complete git history from the original branch."

# Merge into main branch with history preservation
git checkout main
git merge migrate-18.0 --allow-unrelated-histories -m "Merge 18.0 branch history into v18 folder

This merge brings in the complete history from branch '18.0' 
from the source repository into the 'v18' folder structure.
All original commits, authors, and timestamps are preserved."

# Clean up temporary branch
git branch -D migrate-18.0
```

### Repeat for All Branches with History
```bash
# For master branch
git checkout -b migrate-master source-repo/master
mkdir -p master-temp
find . -maxdepth 1 -not -name . -not -name .. -not -name ".git" -not -name "master-temp" -exec mv {} master-temp/ \;
mv master-temp master
git add . && git commit -m "Reorganize master branch content into master folder (preserving history)"
git checkout main && git merge migrate-master --allow-unrelated-histories -m "Merge master branch history"
git branch -D migrate-master

# For 17.0 branch
git checkout -b migrate-17.0 source-repo/17.0
mkdir -p v17-temp
find . -maxdepth 1 -not -name . -not -name .. -not -name ".git" -not -name "v17-temp" -exec mv {} v17-temp/ \;
mv v17-temp v17
git add . && git commit -m "Reorganize 17.0 branch content into v17 folder (preserving history)"
git checkout main && git merge migrate-17.0 --allow-unrelated-histories -m "Merge 17.0 branch history"
git branch -D migrate-17.0

# For 16.0 branch
git checkout -b migrate-16.0 source-repo/16.0
mkdir -p v16-temp
find . -maxdepth 1 -not -name . -not -name .. -not -name ".git" -not -name "v16-temp" -exec mv {} v16-temp/ \;
mv v16-temp v16
git add . && git commit -m "Reorganize 16.0 branch content into v16 folder (preserving history)"
git checkout main && git merge migrate-16.0 --allow-unrelated-histories -m "Merge 16.0 branch history"
git branch -D migrate-16.0

# For 15.0 branch
git checkout -b migrate-15.0 source-repo/15.0
mkdir -p v15-temp
find . -maxdepth 1 -not -name . -not -name .. -not -name ".git" -not -name "v15-temp" -exec mv {} v15-temp/ \;
mv v15-temp v15
git add . && git commit -m "Reorganize 15.0 branch content into v15 folder (preserving history)"
git checkout main && git merge migrate-15.0 --allow-unrelated-histories -m "Merge 15.0 branch history"
git branch -D migrate-15.0
```

### Final Commands for Option B
```bash
# Push all changes with complete history to remote
git push origin main

# Verify history preservation
echo "Verifying history preservation:"
git log --oneline --all | head -20

# Remove source remote (optional)
git remote remove source-repo
```

### Verification Commands
```bash
# Check that all original commits are present
git log --all --grep="Original branch"

# View complete history
git log --oneline --graph --all

# Check each folder has proper content
ls -la master/ v18/ v17/ v16/ v15/
```

---

## Result Structure (Both Options)

```
target-repo/
├── master/     # Content from master branch
├── v18/        # Content from 18.0 branch  
├── v17/        # Content from 17.0 branch
├── v16/        # Content from 16.0 branch
└── v15/        # Content from 15.0 branch
```

## Which Option Should You Choose?

**Choose Option A (File Copy)** if:
- You only need the current state of files from each branch
- You want simple, fast commands
- Git history is not important for your use case

**Choose Option B (History Preservation)** if:
- You need complete commit history, author information, and timestamps
- You want GitHub Copilot to understand the full development context
- You need to preserve audit trails and development patterns