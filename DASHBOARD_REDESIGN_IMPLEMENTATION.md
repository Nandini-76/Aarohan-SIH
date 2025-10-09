# Dashboard Redesign Implementation Guide

## Status: In Progress - Backend Complete, Frontend Partially Complete

## ✅ Completed Components

### Backend API Endpoints (100% Complete)
All required API endpoints have been implemented in `backend/app/main.py`:

1. **GET /api/departments** - List all departments with summary stats
2. **GET /api/departments/{deptId}** - Department details with year breakdown
3. **GET /api/departments/{deptId}/years/{yearNo}** - Year details with section breakdown
4. **GET /api/departments/{deptId}/years/{yearNo}/students** - Student list with filters
5. **GET /api/departments/{deptId}/years/{yearNo}/sections** - Section statistics

**Helper Function**: `load_student_data()` - Loads from comprehensive_predicted.csv with fallbacks

### Frontend Components (40% Complete)
✅ **DepartmentCard.tsx** - Clickable department cards with:
- Department name and icon
- Student count
- Risk distribution badges
- Average CGPA and attendance
- Performance progress bar
- Hover animations

✅ **DepartmentDetail.tsx** - Department page with:
- Breadcrumb navigation
- Summary statistics cards
- Year cards (clickable to navigate to year detail)
- Risk distribution pie chart
- Year-wise CGPA comparison bar chart

## 🚧 Remaining Implementation

### Frontend Pages Needed

#### 1. YearDetail.tsx (Priority: HIGH)
**Location**: `frontend/src/pages/YearDetail.tsx`

**Features Required**:
- Tabs: Overview, Sections, Students
- Overview tab: CGPA histogram, attendance trends, risk pie chart
- Sections tab: Section cards with mini risk charts
- Students tab: Compact student table with search/filter
- Breadcrumb: Dashboard → Department → Year

**Implementation Outline**:
```tsx
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import StudentTable from '../components/StudentTable';
import SectionCard from '../components/SectionCard';
import { BarChart, PieChart, LineChart } from 'recharts';

const YearDetail = () => {
  const { deptId, yearNo } = useParams();
  // Fetch data from /api/departments/{deptId}/years/{yearNo}
  // Render tabs with charts and tables
};
```

#### 2. StudentTable.tsx (Priority: HIGH)
**Location**: `frontend/src/components/StudentTable.tsx`

**Features Required**:
- Columns: Name, Enrollment, Section, CGPA, Attendance, Backlogs, Risk Phase, Status
- Search bar (name/enrollment)
- Filter dropdowns (section, risk phase)
- Click row → open student detail modal/drawer
- Sortable columns
- CSV export button

**Implementation Outline**:
```tsx
import { Table, TableHeader, TableBody, TableRow, TableCell } from './ui/table';
import { Input } from './ui/input';
import { Select } from './ui/select';
import { Button } from './ui/button';
import { Download } from 'lucide-react';

const StudentTable = ({ students, onStudentClick }) => {
  // Search and filter state
  // Sort functionality
  // CSV export function
  // Render table with clickable rows
};
```

#### 3. Chart Components (Priority: MEDIUM)
**Location**: `frontend/src/components/charts/`

Create reusable chart components:

**RiskPieChart.tsx**:
```tsx
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

export const RiskPieChart = ({ data }) => {
  const COLORS = { Red: '#ef4444', Orange: '#f97316', Yellow: '#eab308', Green: '#22c55e' };
  // Render pie chart with risk colors
};
```

**CgpaHistogram.tsx**:
```tsx
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';

export const CgpaHistogram = ({ data }) => {
  // Render CGPA distribution histogram
};
```

**AttendanceTrendLine.tsx**:
```tsx
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

export const AttendanceTrendLine = ({ data }) => {
  // Render attendance trend by risk phase
};
```

**MiniRiskBar.tsx**:
```tsx
export const MiniRiskBar = ({ risk }) => {
  // Compact horizontal bar showing risk distribution
};
```

#### 4. SectionCard.tsx (Priority: MEDIUM)
**Location**: `frontend/src/components/SectionCard.tsx`

**Features**:
- Section name
- Student count
- Average metrics (CGPA, attendance, backlogs)
- Mini risk distribution chart
- Click to expand/filter students by section

#### 5. Updated Dashboard.tsx (Priority: HIGH)
**Location**: `frontend/src/pages/Dashboard.tsx`

**Required Changes**:
- Remove department dropdown
- Add grid of DepartmentCard components
- Fetch data from `/api/departments`
- Keep existing analytics if needed
- Add view toggle: "Department View" vs "Analytics View"

**Implementation**:
```tsx
const Dashboard = () => {
  const [departments, setDepartments] = useState([]);
  const [viewMode, setViewMode] = useState<'departments' | 'analytics'>('departments');
  
  useEffect(() => {
    fetchDepartments();
  }, []);
  
  const fetchDepartments = async () => {
    const response = await fetch(`${API_URL}/api/departments`);
    const data = await response.json();
    setDepartments(data.departments);
  };
  
  return (
    <div>
      {viewMode === 'departments' && (
        <div className="grid grid-cols-2 gap-6">
          {departments.map(dept => (
            <DepartmentCard key={dept.id} {...dept} />
          ))}
        </div>
      )}
      {viewMode === 'analytics' && (
        <AnalyticsOverview students={allStudents} />
      )}
    </div>
  );
};
```

### Routing Updates Required
**Location**: `frontend/src/App.tsx`

Add new routes:
```tsx
<Route path="/department/:deptId" element={<DepartmentDetail />} />
<Route path="/department/:deptId/year/:yearNo" element={<YearDetail />} />
```

## 📊 Data Flow

```
Main Dashboard (/dashboard)
    ↓ (GET /api/departments)
    ├─ Department Cards (Grid)
    │
Department Detail (/department/btech)
    ↓ (GET /api/departments/btech)
    ├─ Summary Stats
    ├─ Year Cards (1-4)
    ├─ Department Analytics (Pie, Bar charts)
    │
Year Detail (/department/btech/year/2)
    ↓ (GET /api/departments/btech/years/2)
    ├─ Tabs: Overview | Sections | Students
    ├─ Overview: CGPA Histogram, Attendance Trend, Risk Pie
    ├─ Sections: Section Cards with mini charts
    ├─ Students: Table with search/filter
        ↓ (GET /api/departments/btech/years/2/students?search=...)
        └─ Click row → Student Detail Modal
```

## 🎨 UI/UX Enhancements to Add

### Loading States
- Skeleton loaders for cards
- Shimmer effect while fetching
- Smooth transitions between pages

### Sticky Summary Bar
Add to YearDetail page:
```tsx
<div className="sticky top-0 z-10 bg-background/95 backdrop-blur border-b p-4">
  <div className="flex gap-6">
    <span>CGPA: 7.2</span>
    <span>Attendance: 74%</span>
    <span>45 at risk</span>
  </div>
</div>
```

### CSV Export
Add to StudentTable:
```tsx
const exportToCSV = () => {
  const csv = [
    ['Name', 'Enrollment', 'CGPA', 'Attendance', 'Risk'].join(','),
    ...students.map(s => [s.name, s.enrollmentNo, s.cgpa, s.attendance, s.riskPhase].join(','))
  ].join('\n');
  
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `students_${deptId}_year_${yearNo}.csv`;
  link.click();
};
```

### Responsive Design
- Mobile: 1 column card layout
- Tablet: 2 columns
- Desktop: 4 columns for year cards
- Collapsible sections on mobile

## 🧪 Testing Checklist

- [ ] Navigate from Dashboard → Department → Year → Student
- [ ] All charts render correctly
- [ ] Data aggregations match backend calculations
- [ ] Search and filters work properly
- [ ] CSV export generates valid files
- [ ] Responsive layout on mobile/tablet
- [ ] Loading states display properly
- [ ] Error handling for failed API calls
- [ ] Back navigation maintains state
- [ ] Breadcrumbs work correctly

## 🚀 Deployment Steps

1. **Test Backend Endpoints**:
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   # Visit http://localhost:8000/docs to test API
   ```

2. **Update Frontend API URL**:
   ```bash
   # frontend/.env
   VITE_API_URL=https://your-backend-url.com
   ```

3. **Build and Deploy**:
   ```bash
   cd frontend
   npm run build
   vercel --prod
   ```

4. **Verify**:
   - Test all navigation paths
   - Check responsive design
   - Verify charts display data correctly

## 📝 Next Steps (Priority Order)

1. ✅ Backend API endpoints - COMPLETE
2. ✅ DepartmentCard component - COMPLETE  
3. ✅ DepartmentDetail page - COMPLETE
4. ⏳ Update Dashboard.tsx to use DepartmentCards
5. ⏳ Create YearDetail.tsx with tabs
6. ⏳ Create StudentTable.tsx
7. ⏳ Create chart components (Pie, Bar, Line)
8. ⏳ Create SectionCard.tsx
9. ⏳ Add routing in App.tsx
10. ⏳ Polish UI (loading, sticky bar, export)
11. ⏳ Test complete flow
12. ⏳ Deploy to production

## 🔗 Related Files

- Backend: `backend/app/main.py` (lines 1706-2126)
- Department Card: `frontend/src/components/DepartmentCard.tsx`
- Department Detail: `frontend/src/pages/DepartmentDetail.tsx`
- Current Dashboard: `frontend/src/pages/Dashboard.tsx`
- Types: `frontend/src/types/index.ts`

## 💡 Tips for Implementation

1. **Start with routing**: Add routes first, then implement pages
2. **Reuse existing components**: Use Card, Badge, Button from ui/
3. **Test API endpoints first**: Use Postman or browser to verify responses
4. **Use React Query**: Cache API responses for better performance
5. **Add error boundaries**: Wrap components to catch rendering errors
6. **Implement incrementally**: Deploy each completed feature
7. **Keep consistent styling**: Use Tailwind classes from existing components

## 🎯 Success Criteria

✓ Users can navigate: Dashboard → Dept → Year → Student details
✓ All 4 years visible for BTech (640 students total)
✓ Charts render correctly with live data
✓ Table is searchable and filterable
✓ Mobile responsive design works
✓ No console errors
✓ Performance < 3s page load
