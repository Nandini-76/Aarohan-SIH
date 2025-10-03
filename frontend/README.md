# AAROHAN Frontend

**React + TypeScript** dashboard for the AAROHAN Student Dropout Prediction & Counseling System.

## 📋 Overview

The AAROHAN frontend provides an intuitive, responsive interface for counselors, administrators, and faculty to:
- Monitor student dropout risk in real-time
- View detailed student profiles with performance trends
- Run what-if simulations to test intervention strategies
- Track post-intervention progress
- Visualize risk distribution across departments

---

## 🛠️ Tech Stack

- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui (Radix UI primitives)
- **Charts**: Recharts
- **Routing**: React Router v6
- **API Client**: Axios
- **State Management**: React Context API
- **Icons**: Lucide React

---

## 📁 Project Structure

```
frontend/
├── src/
│   ├── pages/                # Route components
│   │   ├── Landing.tsx       # Landing page
│   │   ├── Dashboard.tsx     # Main dashboard with risk overview
│   │   ├── StudentProfile.tsx # Individual student details
│   │   ├── Simulation.tsx    # What-if scenario simulator
│   │   ├── Profile.tsx       # User profile page
│   │   ├── About.tsx         # About the system
│   │   └── Contact.tsx       # Contact page
│   │
│   ├── components/           # Reusable components
│   │   ├── RiskBadge.tsx     # Color-coded risk indicators
│   │   ├── DashboardLayout.tsx # Main layout wrapper
│   │   ├── Sidebar.tsx       # Navigation sidebar
│   │   ├── SiteHeader.tsx    # Top navigation header
│   │   ├── LoadingSpinner.tsx # Loading states
│   │   ├── ErrorBoundary.tsx # Error handling
│   │   └── ui/               # shadcn/ui components
│   │       ├── button.tsx
│   │       ├── card.tsx
│   │       ├── badge.tsx
│   │       ├── input.tsx
│   │       ├── slider.tsx
│   │       └── ... (30+ components)
│   │
│   ├── services/             # API integration
│   │   ├── api.ts            # Backend API client
│   │   └── renderPing.ts     # Health check service
│   │
│   ├── contexts/             # React contexts
│   │   └── AuthContext.tsx   # Authentication state
│   │
│   ├── hooks/                # Custom React hooks
│   │   ├── use-toast.ts      # Toast notifications
│   │   └── use-mobile.tsx    # Responsive detection
│   │
│   ├── lib/                  # Utilities
│   │   └── utils.ts          # Helper functions (cn, etc.)
│   │
│   ├── types/                # TypeScript types
│   │   └── index.ts          # Shared type definitions
│   │
│   ├── App.tsx               # Root component with routing
│   ├── main.tsx              # Entry point
│   └── index.css             # Global styles + Tailwind
│
├── public/                   # Static assets
│   └── assets/               # Images, logos
│
├── components.json           # shadcn/ui configuration
├── tailwind.config.ts        # Tailwind CSS config
├── vite.config.ts            # Vite build config
├── tsconfig.json             # TypeScript config
└── package.json              # Dependencies

```

---

## 🚀 Getting Started

### Prerequisites

- **Node.js** 18+ and npm/yarn/pnpm/bun
- Backend API running (see main [README.md](../README.md))

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create environment file
echo "VITE_API_BASE_URL=http://localhost:8000" > .env

# Start development server
npm run dev
```

The app will be available at **http://localhost:5173**

### Environment Variables

Create `.env` file in `frontend/` directory:

```bash
# Backend API URL
VITE_API_BASE_URL=http://localhost:8000

# Optional: Feature flags
VITE_ENABLE_MOCK_DATA=false
```

---

## 📄 Pages Overview

### 1. Landing Page (`/`)
- Hero section with system overview
- Key features showcase
- Call-to-action for dashboard access
- Responsive design with animated sections

### 2. Dashboard (`/dashboard`)
- **Risk Distribution Cards**: Green/Yellow/Orange/Red counts
- **Student List**: Searchable, filterable table
- **Risk Badges**: Color-coded indicators
- **Quick Actions**: View profile, simulate scenarios
- **Statistics**: Total students, intervention success rates

### 3. Student Profile (`/student/:id`)
- **Personal Information**: Name, enrollment, department
- **Academic Metrics**: CGPA, attendance, backlogs
- **Risk Assessment**: Current phase with explanation
- **Performance Trends**: Line charts showing CGPA/attendance over time
- **Post-Intervention Progress**: Before/after comparison graphs
- **Intervention History**: Timeline of counseling sessions
- **Actions**: Edit, simulate, mark intervention

### 4. Simulation Page (`/simulation`)
- **Interactive Parameter Adjustment**:
  - Attendance slider (0-100%)
  - CGPA slider (0-10.0)
  - Backlogs input
  - Fee payment toggle
  - Suspension flag toggle
- **Real-Time Prediction**: Shows how changes affect risk level
- **What-If Scenarios**: Test intervention strategies
- **Side-by-Side Comparison**: ML prediction vs. rule-based override
- **Recommendations**: Suggested actions based on risk level

### 5. Profile Page (`/profile`)
- User account information
- System settings
- Notification preferences

### 6. About Page (`/about`)
- System overview and methodology
- Contact information
- Technical details

---

## 🎨 Components

### Core Components

#### RiskBadge
Color-coded badges for risk visualization:
```tsx
<RiskBadge 
  phase="Orange"     // Green | Yellow | Orange | Red
  size="lg"          // sm | md | lg
  showIcon={true}    // Display warning icon
/>
```

#### DashboardLayout
Wrapper for authenticated pages with sidebar:
```tsx
<DashboardLayout>
  <YourPageContent />
</DashboardLayout>
```

#### LoadingSpinner
Consistent loading states:
```tsx
<LoadingSpinner text="Loading students..." />
```

### UI Components (shadcn/ui)

All components follow Radix UI primitives with Tailwind styling:

- **Forms**: `<Button>`, `<Input>`, `<Select>`, `<Switch>`, `<Slider>`
- **Data Display**: `<Card>`, `<Badge>`, `<Table>`, `<Avatar>`
- **Feedback**: `<Alert>`, `<Toast>`, `<Progress>`, `<Skeleton>`
- **Overlay**: `<Dialog>`, `<Sheet>`, `<Popover>`, `<Tooltip>`
- **Navigation**: `<Tabs>`, `<Accordion>`, `<NavigationMenu>`

---

## 🔌 API Integration

### API Service (`src/services/api.ts`)

```typescript
import { studentApi } from '@/services/api';

// Fetch all students
const students = await studentApi.getAll();

// Get student by enrollment number
const student = await studentApi.getById('2023CSE045');

// Run prediction simulation
const result = await studentApi.simulate({
  enrollment_no: '2023CSE045',
  attendance: 75.0,
  cgpa: 6.5,
  backlogs: 2,
  // ... other fields
});

// Get dashboard statistics
const stats = await studentApi.getDashboardStats();
```

### API Endpoints Used

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/students` | Fetch all students |
| GET | `/api/students/:id` | Get student details |
| POST | `/api/predict` | Run risk prediction |
| POST | `/api/simulate` | Run what-if simulation |
| GET | `/api/dashboard/stats` | Get overview statistics |

---

## 🎨 Styling

### Tailwind CSS

Custom theme configuration in `tailwind.config.ts`:

```typescript
export default {
  theme: {
    extend: {
      colors: {
        primary: {...},    // Brand blue
        secondary: {...},  // Accent colors
        destructive: {...}, // Error states
        // Risk colors
        green: '#22c55e',
        yellow: '#eab308',
        orange: '#f97316',
        red: '#ef4444',
      },
    },
  },
}
```

### CSS Variables

Global styles in `src/index.css`:
```css
:root {
  --primary: 221.2 83.2% 53.3%;
  --destructive: 0 84.2% 60.2%;
  /* ... other variables */
}
```

---

## 📦 Build & Deployment

### Development Build

```bash
npm run dev
```

### Production Build

```bash
npm run build

# Output: dist/ directory
# Preview build locally:
npm run preview
```

### Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod

# Or use Vercel GitHub integration (auto-deploy on push)
```

See [DEPLOYMENT.md](../DEPLOYMENT.md) for complete deployment guide.

---

## 🧪 Testing

### Run Tests

```bash
# Unit tests
npm run test

# Coverage report
npm run test:coverage
```

### Manual Testing Checklist

- [ ] Dashboard loads with mock/real data
- [ ] Student search and filtering works
- [ ] Risk badges display correct colors
- [ ] Student profile shows complete information
- [ ] Performance charts render correctly
- [ ] Simulation page adjusts parameters smoothly
- [ ] Real-time risk updates work
- [ ] Mobile responsive layout functions properly
- [ ] Error states display appropriately
- [ ] Loading states show during API calls

---

## 🔧 Development Tips

### Adding New Components

Use shadcn/ui CLI:
```bash
npx shadcn-ui@latest add [component-name]

# Example:
npx shadcn-ui@latest add calendar
```

### Code Style

- **TypeScript**: Strict mode enabled
- **ESLint**: Configured for React + TypeScript
- **Prettier**: Auto-formatting on save
- **Imports**: Use `@/` alias for src directory

### Performance Optimization

1. **Lazy Loading**: Pages are code-split automatically
2. **Image Optimization**: Use next-gen formats (WebP)
3. **Bundle Analysis**: 
   ```bash
   npm run build -- --analyze
   ```
4. **Memoization**: Use `React.memo()` for expensive components

---

## 📱 Responsive Design

Mobile-first approach with breakpoints:

```typescript
// Tailwind breakpoints
sm: '640px',   // Mobile landscape
md: '768px',   // Tablet
lg: '1024px',  // Desktop
xl: '1280px',  // Large desktop
2xl: '1536px'  // Extra large
```

### Mobile Navigation

- Hamburger menu on mobile
- Full sidebar on desktop
- Touch-friendly interactions
- Optimized charts for small screens

---

## 🤝 Contributing

1. Follow TypeScript strict mode
2. Use functional components with hooks
3. Add prop types for all components
4. Write descriptive commit messages
5. Test on mobile and desktop

---

## 📚 Resources

- **React Documentation**: https://react.dev/
- **Vite Guide**: https://vitejs.dev/guide/
- **Tailwind CSS**: https://tailwindcss.com/docs
- **shadcn/ui**: https://ui.shadcn.com/
- **Recharts**: https://recharts.org/

---

## 📄 License

MIT License - see [LICENSE](../LICENSE) for details

---

**Built with ❤️ using modern React best practices**
