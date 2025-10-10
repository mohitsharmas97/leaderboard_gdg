# Quick Fix: Reduce Badge Update Delay

## Current Situation
- Updates take **~40 minutes on average** (up to 74 minutes)
- GitHub Actions runs **every 1 hour**

## How to Speed Up Updates

### Option 1: Every 15 Minutes (Recommended)
Edit `.github/workflows/update-leaderboard.yml`:

```yaml
on:
  schedule:
    - cron: '*/15 * * * *'  # Changed from '0 */1 * * *'
  workflow_dispatch:
```

**Result:** Updates every 15 minutes, average delay drops to ~15 minutes

### Option 2: Every 30 Minutes (Balanced)
```yaml
on:
  schedule:
    - cron: '*/30 * * * *'
  workflow_dispatch:
```

**Result:** Updates every 30 minutes, average delay ~23 minutes

### Option 3: Manual Trigger (Instant)
1. Go to your repository on GitHub
2. Click "Actions" tab
3. Click "Update Leaderboard Data" workflow
4. Click "Run workflow" button
5. Wait 1-2 minutes for scraper to complete

**Result:** Instant update on demand

## Implementation Steps

1. Open `.github/workflows/update-leaderboard.yml`
2. Change line 4 from:
   ```yaml
   - cron: '0 */1 * * *'
   ```
   to:
   ```yaml
   - cron: '*/15 * * * *'
   ```
3. Commit and push changes
4. Done! Updates now run every 15 minutes

## Cost Considerations

### GitHub Actions Free Tier:
- **2,000 minutes/month** for free accounts
- **3,000 minutes/month** for Pro accounts

### Usage Calculation:
| Frequency | Runs/Day | Runs/Month | Minutes/Month (est.) |
|-----------|----------|------------|----------------------|
| 1 hour    | 24       | 720        | ~360 (safe)          |
| 30 min    | 48       | 1,440      | ~720 (safe)          |
| 15 min    | 96       | 2,880      | ~1,440 (needs Pro)   |
| 10 min    | 144      | 4,320      | ~2,160 (needs Pro)   |

**Recommendation:** Use 30-minute interval for free accounts, 15-minute for Pro

## Why Not Faster?

### 5 Minutes or Less:
- ❌ Very expensive (uses up GitHub Actions quota quickly)
- ❌ Risk of hitting Google API rate limits
- ❌ Might get IP banned
- ❌ Unnecessary for most use cases

### Real-World Timing:
- Google's API itself takes 5-10 minutes to sync new badges
- Running scraper every 5 minutes won't make it faster than Google's sync time
- Sweet spot is **15-30 minutes**
