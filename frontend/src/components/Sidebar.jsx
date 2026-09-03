import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Upload, 
  ClipboardCheck, 
  BookOpen, 
  FileCheck, 
  UserCheck, 
  Settings,
  ShieldCheck,
  ChevronRight
} from 'lucide-react';

export default function Sidebar() {
  const navSections = [
    {
      header: 'DOCUMENTS',
      items: [
        { to: '/upload', label: 'Upload TRF Document', icon: Upload },
      ]
    },
    {
      header: 'EVALUATIONS',
      items: [
        { to: '/evaluations', label: 'All Evaluations', icon: ClipboardCheck },
      ]
    },
    {
      header: 'KNOWLEDGE BASE',
      items: [
        { to: '/standards', label: 'Standards & Rules', icon: BookOpen },
        { to: '/reports', label: 'Evaluation Reports', icon: FileCheck },
      ]
    },
    {
      header: 'WORKFLOW',
      items: [
        { to: '/certifier', label: 'Certifier Queue', icon: UserCheck },
      ]
    },
    {
      header: 'SYSTEM',
      items: [
        { to: '/settings', label: 'System Settings', icon: Settings },
      ]
    }
  ];

  return (
    <aside className="w-64 bg-[#080c16] text-slate-300 border-r border-slate-800/80 flex flex-col h-screen sticky top-0 shrink-0 select-none">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800/80 flex items-center gap-3.5">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-500 via-indigo-500 to-cyan-400 flex items-center justify-center shadow-lg shadow-indigo-500/25 text-white">
          <ShieldCheck className="w-6 h-6" />
        </div>
        <div>
          <h1 className="font-bold text-white tracking-tight text-lg leading-tight flex items-center gap-1">
            MedVerify <span className="text-transparent bg-clip-text bg-gradient-to-r from-sky-400 to-indigo-400">AI</span>
          </h1>
          <p className="text-[11px] text-slate-400 font-medium tracking-wide">Evaluation Assistant</p>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 overflow-y-auto p-4 space-y-6">
        {/* Dashboard Main Link */}
        <NavLink
          to="/"
          end
          className={({ isActive }) =>
            `flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-semibold transition-all ${
              isActive
                ? 'bg-gradient-to-r from-indigo-600 to-blue-600 text-white shadow-md shadow-indigo-600/30'
                : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/50'
            }`
          }
        >
          <LayoutDashboard className="w-4 h-4" />
          <span>Dashboard</span>
        </NavLink>

        {/* Categorized Nav Sections */}
        {navSections.map((section, idx) => (
          <div key={idx} className="space-y-1.5">
            <h3 className="px-3 text-[11px] font-semibold text-slate-400 tracking-wider flex items-center gap-1.5 font-mono uppercase">
              <span>{section.header}</span>
              <span className="w-1.5 h-1.5 rounded-full bg-indigo-500/80 inline-block"></span>
            </h3>
            {section.items.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3.5 py-2 rounded-xl text-xs font-medium transition-all ${
                    isActive
                      ? 'bg-gradient-to-r from-indigo-600 to-blue-600 text-white font-semibold shadow-md shadow-indigo-600/30'
                      : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/40'
                  }`
                }
              >
                <item.icon className="w-4 h-4" />
                <span>{item.label}</span>
              </NavLink>
            ))}
          </div>
        ))}
      </nav>

      {/* Bottom User Profile Widget */}
      <div className="p-4 border-t border-slate-800/80 bg-[#060911]">
        <div className="bg-[#0d1322] border border-slate-800/80 rounded-xl p-3 flex items-center justify-between hover:border-slate-700 transition cursor-pointer">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-emerald-500 to-teal-400 text-white font-bold text-xs flex items-center justify-center shadow-sm">
              MA
            </div>
            <div>
              <div className="text-xs font-bold text-slate-200">Admin User</div>
              <div className="text-[10px] text-slate-400">System Administrator</div>
            </div>
          </div>
          <ChevronRight className="w-4 h-4 text-slate-500" />
        </div>
      </div>
    </aside>
  );
}
