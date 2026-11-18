# Publish to Jeffrey's GitHub

Suggested repository name: `customer-churn-retention-analytics`

Suggested About description:

> Exploring customer churn across 7,043 IBM Telco records, with SQL Server analysis, Power BI measures and reproducible dashboard previews.

## Create the empty repository

1. Sign in as `Emrae77` and open [GitHub's new repository page](https://github.com/new).
2. Enter `customer-churn-retention-analytics`, add the description above and choose Public.
3. Leave the options to add a README, .gitignore and license unselected. This package already contains its README and .gitignore.
4. Create the repository.

## Upload from the Mac terminal

Extract the ZIP and move the `customer-churn-retention-analytics` folder into `/Users/new/Desktop/Projects/`. Run these commands from that extracted folder, not the existing BankOps AI folder:

```bash
cd /Users/new/Desktop/Projects/customer-churn-retention-analytics
git init
git branch -M main
git add .
git --no-pager status --short
git commit -m "Add Telco churn analysis, dashboard previews and documentation"
git remote add origin https://github.com/Emrae77/customer-churn-retention-analytics.git
git push -u origin main
```

If Git reports that `origin` already exists, inspect it with `git remote -v`. If it is this same repository, continue with the push. If it points elsewhere, stop and check that the terminal is in the newly extracted Telco project folder.

Do not force-push or overwrite an existing unrelated repository. The package has no `.git` history, customer-level CSVs, API keys or database credentials. No generation step is required just to publish the supplied figures and code.

After the push succeeds, review the rendered README and all three images at:

`https://github.com/Emrae77/customer-churn-retention-analytics`

That URL is the intended destination, not a claim that the repository already exists. Pin it on your profile beside BankOps AI and Contact Centre Performance Analytics.

## Add the original Power BI report when available

The included PNGs are original static dashboard previews generated from IBM data. To demonstrate the finished Power BI report itself, add your actual `.pbix` or `.pbip` project and exports from that report. Follow `powerbi/README.md`, run the validation cases, then label those files as Power BI exports. Keep the distinction clear in the README.
