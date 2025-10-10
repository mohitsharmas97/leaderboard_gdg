# Leaderboard Fixes Applied

## ✅ HIGH PRIORITY FIXES IMPLEMENTED

### 1. **CSV Data Source Fixed**
- **Before:** Fetching from external repository `mohitsharmas97/leaderboard_gdg`
- **After:** Using local `./progress_data.csv` file
- **Why:** Ensures data reliability and removes external dependency

### 2. **Input Sanitization Added (XSS Protection)**
- **What:** Created `sanitizeHTML()` function
- **Where:** Applied to user names and completion times before rendering
- **How:** Uses `textContent` to escape HTML entities
```javascript
function sanitizeHTML(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}
```

### 3. **Improved CSV Parsing with Validation**
- **Added:** Empty row detection (not just blank lines, but rows with only commas)
- **Added:** Username validation (rows without names are skipped)
- **Added:** Better data validation for malformed CSV rows
```javascript
// Skip empty lines or lines with only commas
if (!line || line.replace(/,/g, '').trim() === '') continue;

// Validate row has at least some data
if (values.every(v => v === '')) continue;

// Only add row if it has a username (required field)
if (row['User Name'] && row['User Name'].trim() !== '') {
    data.push(row);
}
```

### 4. **Cache Busting Added**
- **What:** Added timestamp parameter to CSV fetch
- **Why:** Prevents browser caching of old data
- **Result:** Users see updates immediately after refresh
```javascript
const cacheBuster = new Date().getTime();
fetch(`./progress_data.csv?v=${cacheBuster}`)
```

## ✅ MEDIUM PRIORITY FIXES IMPLEMENTED

### 5. **Search Debouncing (300ms)**
- **Before:** Search executed on every keystroke
- **After:** 300ms delay before executing search
- **Benefit:** Reduces unnecessary rendering and improves performance
- **Impact:** Especially helpful with large datasets (100+ participants)

---

## ⏰ WHY BADGE UPDATES TAKE ~1 HOUR TO APPEAR

### The Update Pipeline:

```
User completes badge on Google Cloud
           ↓
    (Takes a few minutes to sync in Google's system)
           ↓
GitHub Actions runs every 1 hour (cron: '0 */1 * * *')
           ↓
Scraper fetches data from Google Cloud API
           ↓
New CSV is committed to repository
           ↓
User refreshes leaderboard website
           ↓
Badge appears on leaderboard
```

### Root Causes:

1. **GitHub Actions Schedule: Every 1 Hour**
   ```yaml
   schedule:
     - cron: '0 */1 * * *'  # Runs at minute 0 of every hour
   ```
   - If you complete a badge at 10:05 AM, the next scraper run is at 11:00 AM
   - **Maximum delay: 59 minutes**
   - **Average delay: ~30 minutes**

2. **Google Cloud API Sync Time**
   - Google's system takes 5-10 minutes to update your public profile
   - Even if scraper runs immediately, it might not see the new badge yet

3. **GitHub Pages Deployment**
   - After CSV is updated, GitHub Pages may take 1-5 minutes to deploy changes
   - Browser cache (now fixed with cache busting)

### Total Delay Breakdown:
```
Google API sync:        5-10 minutes
Wait for next cron:     0-59 minutes (avg: 30 min)
GitHub Pages deploy:    1-5 minutes
Browser cache:          0 min (fixed with cache busting)
-------------------------------------------
TOTAL:                  6-74 minutes (avg: ~40 minutes)
```

### How to Reduce Delay:

#### Option 1: Increase Scraper Frequency (Recommended)
Change the workflow to run every 15 minutes:
```yaml
schedule:
  - cron: '*/15 * * * *'  # Every 15 minutes
```
**New average delay: ~15 minutes**

#### Option 2: Run Every 30 Minutes (Balanced)
```yaml
schedule:
  - cron: '*/30 * * * *'  # Every 30 minutes
```
**New average delay: ~23 minutes**

#### Option 3: Manual Trigger (Instant)
- Users can trigger update manually using GitHub Actions
- Already available via `workflow_dispatch` in your workflow
- Navigate to: Repository → Actions → "Update Leaderboard Data" → "Run workflow"

### Why Not Run Every Minute?
1. **GitHub Actions Limits:** 
   - 2,000 minutes/month for free accounts
   - Running every minute = 43,200 runs/month (way over limit)
   
2. **API Rate Limits:**
   - Google Cloud API might rate limit your scraper
   - Could get IP banned for too many requests

3. **Unnecessary Load:**
   - Most users don't complete badges every minute
   - 15-minute intervals are reasonable

---

## 🎯 RECOMMENDED NEXT STEPS

### To Improve Update Speed:
1. **Change cron schedule to every 15 minutes** (see Option 1 above)
2. **Add a "Last Updated" countdown timer** showing when next update will happen
3. **Add manual refresh button** that triggers the GitHub Action workflow

### Optional Enhancements (Not Implemented):
- Add loading states during fetch
- Add error retry logic (3 attempts)
- Add webhook integration for instant updates (requires backend)
- Add progressive web app (PWA) for offline support

---

## 📊 Performance Improvements Applied

| Issue | Before | After | Impact |
|-------|--------|-------|--------|
| CSV Source | External repo | Local file | More reliable |
| XSS Protection | None | Sanitized | Secure |
| Empty rows | Some parsed | All skipped | Cleaner data |
| Search performance | Instant | 300ms debounce | Smoother UX |
| Browser cache | Cached forever | Cache busting | Fresh data |
| Update frequency | Every 1 hour | Every 1 hour* | *Can be reduced |

*To reduce update delay, change the cron schedule in `.github/workflows/update-leaderboard.yml`

---

## 🔍 Issues NOT Fixed (As Per Your Request)

### UI/UX Issues (Excluded):
- ❌ Accessibility (ARIA labels, keyboard navigation)
- ❌ Responsive design for very small screens
- ❌ Dark/light mode toggle

### Data Handling Issues (Excluded):
- ❌ International timezone support
- ❌ Dynamic max progress calculation

### Missing Features (Excluded):
- ❌ Offline support
- ❌ Export to CSV
- ❌ Pagination
- ❌ Data caching with localStorage

All critical security and performance issues have been addressed! ✅
