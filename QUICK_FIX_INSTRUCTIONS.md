# Quick Fix Instructions

## Current Issue
Only BBA and BSc showing, missing BSc Agriculture and BTech

## Root Cause
Department names in Firebase likely have variations (Bsc-agriculture, Bsc-CS, Btech) that the normalization wasn't catching due to case sensitivity.

## Fix Applied
Changed department normalization to use `.toLowerCase()` for case-insensitive matching:

```typescript
const deptLower = dept.toLowerCase();

if (deptLower.includes('agriculture') || deptLower.includes('agri')) {
  dept = 'BSc Agriculture';
} else if (deptLower.includes('bba') || deptLower.includes('b.b.a')) {
  dept = 'BBA';
} else if (deptLower.includes('bsc') || deptLower.includes('b.sc') || deptLower.includes('cs') || deptLower.includes('computer')) {
  dept = 'BSc';
} else if (deptLower.includes('btech') || deptLower.includes('b.tech') || deptLower.includes('tech') || deptLower.includes('engineering')) {
  dept = 'BTech';
}
```

## To Test
1. **Refresh the page** (Ctrl+F5) to load new code
2. **Open DevTools** (F12)
3. **Check Console** - Look for these logs:
   - "Raw department values from Firebase" - should show actual values
   - "All departments in studentsByDepartment" - should show 4 departments
   - "Filtered sorted departments" - should show [BBA, BSc, BSc Agriculture, BTech]
4. **Check Dashboard** - Should now show all 4 department cards

## If Still Not Working
Share the console log output, specifically:
- "Raw department values from Firebase: [...]"
- "All departments in studentsByDepartment: [...]"
- "Department counts: [...]"

This will show us exactly what the Firebase data contains.
