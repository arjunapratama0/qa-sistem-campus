import { Outlet } from "react-router-dom";
import MobileNav from "./MobileNav.jsx";
import Navbar from "./Navbar.jsx";
import Sidebar from "./Sidebar.jsx";

export default function DashboardLayout() {
  return (
    <div className="min-h-screen bg-slate-50">
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="flex min-w-0 flex-1 flex-col">
          <Navbar />
          <main className="flex-1 px-4 pb-24 pt-6 md:px-6 md:pb-6">
            <Outlet />
          </main>
          <MobileNav />
        </div>
      </div>
    </div>
  );
}
