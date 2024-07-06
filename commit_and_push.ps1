# Define variables
$commit_message = "Organize project structure and clean up repository"
$branch_name = "main"  # Change this if your branch name is different
$repo_url = "https://github.com/DBTGPT/Bot.git"  # Change this to your repository URL if different

# Ensure all changes are added to the staging area
git add -A

# Commit the changes with a message
git commit -m $commit_message

# Push the changes to the specified branch
git push origin $branch_name

# Confirm successful push
Write-Output "Code has been successfully committed and pushed to GitHub."
