import { Toaster } from "./components/ui/toaster";
import { Toaster as Sonner } from "./components/ui/sonner";
import { TooltipProvider } from "./components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import DashboardLayout from "./components/DashboardLayout";
import ErrorBoundary from "./components/ErrorBoundary";
import Landing from "./pages/Landing";
import Dashboard from "./pages/Dashboard";
import DepartmentDetail from "./pages/DepartmentDetail";
import YearDetail from "./pages/YearDetail";
import StudentProfile from "./pages/StudentProfile";
import Simulation from "./pages/Simulation";
import Profile from "./pages/Profile";
import NotFound from "./pages/NotFound";
import About from "./pages/About";
import Contact from "./pages/Contact";
import RenderPingStatus from "./components/RenderPingStatus";

// Import render ping service to keep backend alive
import "./services/renderPing";

const queryClient = new QueryClient();

const App = () => (
  <ErrorBoundary>
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <AuthProvider>
          <Toaster />
          <Sonner />
          <BrowserRouter>
            <Routes>
              <Route path="/" element={<Landing />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/department/:deptId" element={<DepartmentDetail />} />
              <Route path="/department/:deptId/year/:yearNo" element={<YearDetail />} />
              <Route path="/student/:enrollmentNo" element={<StudentProfile />} />
              <Route path="/simulation" element={<Simulation />} />
              <Route
                path="/profile"
                element={
                  <DashboardLayout>
                    <Profile />
                  </DashboardLayout>
                }
              />
              <Route path="/about" element={<About />} />
              <Route path="/contact" element={<Contact />} />
              {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
              <Route path="*" element={<NotFound />} />
            </Routes>
          </BrowserRouter>
          {/* Development-only ping status indicator */}
          <RenderPingStatus />
        </AuthProvider>
      </TooltipProvider>
    </QueryClientProvider>
  </ErrorBoundary>
);

export default App;
