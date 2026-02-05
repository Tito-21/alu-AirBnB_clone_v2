"use client"

import { useState } from "react"
import { Search, Filter, Plus, ChevronDown, X, Eye, Calendar, FileText, User, Scale } from "lucide-react"

// Sample case data with more details
interface Case {
  id: number
  firstName: string
  lastName: string
  caseNumber: string
  caseType: string
  status: "Open" | "In Progress" | "Closed" | "Pending"
  dateOpened: string
  description: string
  assignedTo: string
}

const initialCases: Case[] = [
  { 
    id: 1, 
    firstName: "Cedric", 
    lastName: "Manzi", 
    caseNumber: "CW-2026-001",
    caseType: "Civil Dispute",
    status: "Open",
    dateOpened: "2026-01-15",
    description: "Property boundary dispute between neighbors",
    assignedTo: "Judge Uwimana"
  },
  { 
    id: 2, 
    firstName: "Jane", 
    lastName: "Muhoza", 
    caseNumber: "CW-2026-002",
    caseType: "Family Law",
    status: "In Progress",
    dateOpened: "2026-01-18",
    description: "Child custody arrangement proceedings",
    assignedTo: "Judge Habimana"
  },
  { 
    id: 3, 
    firstName: "Robert", 
    lastName: "Kalisa", 
    caseNumber: "CW-2026-003",
    caseType: "Criminal",
    status: "Pending",
    dateOpened: "2026-01-20",
    description: "Fraud investigation and prosecution",
    assignedTo: "Judge Mugabo"
  },
  { 
    id: 4, 
    firstName: "Emille", 
    lastName: "Gakuba", 
    caseNumber: "CW-2026-004",
    caseType: "Commercial",
    status: "Open",
    dateOpened: "2026-01-22",
    description: "Contract breach between business partners",
    assignedTo: "Judge Uwimana"
  },
  { 
    id: 5, 
    firstName: "Michael", 
    lastName: "Rugamba", 
    caseNumber: "CW-2026-005",
    caseType: "Labor Law",
    status: "Closed",
    dateOpened: "2026-01-10",
    description: "Wrongful termination claim resolved",
    assignedTo: "Judge Habimana"
  },
  { 
    id: 6, 
    firstName: "Sarah", 
    lastName: "Mbabzi", 
    caseNumber: "CW-2026-006",
    caseType: "Civil Dispute",
    status: "In Progress",
    dateOpened: "2026-01-25",
    description: "Personal injury compensation case",
    assignedTo: "Judge Mugabo"
  },
]

const filterOptions = {
  caseNumber: ["CW-2026-001", "CW-2026-002", "CW-2026-003", "CW-2026-004", "CW-2026-005", "CW-2026-006"],
  suspect: ["Cedric Manzi", "Robert Kalisa", "Michael Rugamba"],
  victim: ["Jane Muhoza", "Emille Gakuba", "Sarah Mbabazi"],
  names: ["Cedric", "Jane", "Robert", "Emille", "Michael", "Sarah"],
}

const caseTypes = ["Civil Dispute", "Family Law", "Criminal", "Commercial", "Labor Law", "Property Law"]
const judges = ["Judge Uwimana", "Judge Habimana", "Judge Mugabo", "Judge Niyonzima"]

export default function CaseWiseDashboard() {
  const [cases, setCases] = useState<Case[]>(initialCases)
  const [searchQuery, setSearchQuery] = useState("")
  const [activeFilter, setActiveFilter] = useState<string | null>(null)
  const [selectedFilters, setSelectedFilters] = useState<Record<string, string>>({})
  const [currentView, setCurrentView] = useState<"registration" | "myCases" | "laws">("registration")
  const [showRegisterModal, setShowRegisterModal] = useState(false)
  const [selectedCase, setSelectedCase] = useState<Case | null>(null)
  
  // Form state
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    caseType: "",
    description: "",
    assignedTo: "",
  })

  const toggleFilter = (filter: string) => {
    setActiveFilter(activeFilter === filter ? null : filter)
  }

  const selectFilterOption = (filter: string, option: string) => {
    setSelectedFilters((prev) => ({
      ...prev,
      [filter]: prev[filter] === option ? "" : option,
    }))
    setActiveFilter(null)
  }

  const handleRegisterCase = () => {
    if (!formData.firstName || !formData.lastName || !formData.caseType) {
      alert("Please fill in all required fields")
      return
    }

    const newCase: Case = {
      id: cases.length + 1,
      firstName: formData.firstName,
      lastName: formData.lastName,
      caseNumber: `CW-2026-${String(cases.length + 1).padStart(3, "0")}`,
      caseType: formData.caseType,
      status: "Open",
      dateOpened: new Date().toISOString().split("T")[0],
      description: formData.description,
      assignedTo: formData.assignedTo || "Unassigned",
    }

    setCases([...cases, newCase])
    setShowRegisterModal(false)
    setFormData({ firstName: "", lastName: "", caseType: "", description: "", assignedTo: "" })
  }

  const filteredCases = cases.filter((caseItem) => {
    const matchesSearch = 
      caseItem.firstName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      caseItem.lastName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      caseItem.caseNumber.toLowerCase().includes(searchQuery.toLowerCase())
    
    const matchesCaseNumber = !selectedFilters.caseNumber || caseItem.caseNumber === selectedFilters.caseNumber
    const matchesName = !selectedFilters.names || 
      caseItem.firstName === selectedFilters.names || 
      caseItem.lastName === selectedFilters.names

    return matchesSearch && matchesCaseNumber && matchesName
  })

  const getStatusColor = (status: Case["status"]) => {
    switch (status) {
      case "Open": return "bg-emerald-100 text-emerald-700"
      case "In Progress": return "bg-amber-100 text-amber-700"
      case "Closed": return "bg-slate-100 text-slate-700"
      case "Pending": return "bg-sky-100 text-sky-700"
      default: return "bg-slate-100 text-slate-700"
    }
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Navbar */}
      <nav className="bg-slate-800 text-white px-6 py-4 flex items-center justify-between shadow-md">
        <h1 className="text-xl font-semibold flex items-center gap-2">
          <Scale className="w-6 h-6" /> CaseWise
        </h1>
        <button className="bg-slate-700 hover:bg-slate-600 px-4 py-2 rounded-md text-sm transition-colors">
          Logout
        </button>
      </nav>

      <div className="flex">
        {/* Sidebar */}
        <aside className="w-56 bg-white min-h-[calc(100vh-64px)] border-r border-slate-200 p-4">
          <nav className="space-y-1">
            <button
              onClick={() => setCurrentView("registration")}
              className={`w-full text-left block px-4 py-3 rounded-lg font-medium transition-colors ${
                currentView === "registration" 
                  ? "bg-slate-800 text-white" 
                  : "text-slate-600 hover:bg-slate-100"
              }`}
            >
              Case Registration
            </button>
            <button
              onClick={() => setCurrentView("myCases")}
              className={`w-full text-left block px-4 py-3 rounded-lg font-medium transition-colors ${
                currentView === "myCases" 
                  ? "bg-slate-800 text-white" 
                  : "text-slate-600 hover:bg-slate-100"
              }`}
            >
              My Cases
            </button>
            <button
              onClick={() => setCurrentView("laws")}
              className={`w-full text-left block px-4 py-3 rounded-lg font-medium transition-colors ${
                currentView === "laws" 
                  ? "bg-slate-800 text-white" 
                  : "text-slate-600 hover:bg-slate-100"
              }`}
            >
              Laws
            </button>
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-6">
          <div className="max-w-5xl mx-auto">
            
            {/* Case Registration View */}
            {currentView === "registration" && (
              <>
                <h2 className="text-2xl font-semibold text-slate-800 mb-6">Case Management</h2>

                {/* Search and Filters */}
                <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4 mb-6">
                  <div className="flex flex-wrap items-center gap-3">
                    {/* Search Bar */}
                    <div className="relative flex-1 min-w-64">
                      <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                      <input
                        type="text"
                        placeholder="Search cases..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full pl-10 pr-4 py-2.5 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-800 focus:border-transparent transition-all"
                      />
                    </div>

                    {/* Filter Dropdowns */}
                    <div className="flex items-center gap-2 flex-wrap">
                      <div className="flex items-center gap-1 text-slate-500 text-sm">
                        <Filter className="w-4 h-4" />
                        <span>Filters:</span>
                      </div>

                      {(["caseNumber", "suspect", "victim", "names"] as const).map((filter) => (
                        <div key={filter} className="relative">
                          <button
                            onClick={() => toggleFilter(filter)}
                            className={`flex items-center gap-1.5 px-3 py-2 rounded-lg border text-sm transition-all ${
                              selectedFilters[filter]
                                ? "bg-slate-800 text-white border-slate-800"
                                : "bg-white text-slate-600 border-slate-200 hover:border-slate-300"
                            }`}
                          >
                            <span className="capitalize">
                              {filter === "caseNumber" ? "Case Number" : filter}
                            </span>
                            <ChevronDown className={`w-4 h-4 transition-transform ${activeFilter === filter ? "rotate-180" : ""}`} />
                          </button>

                          {/* Dropdown */}
                          {activeFilter === filter && (
                            <div className="absolute top-full left-0 mt-1 w-48 bg-white border border-slate-200 rounded-lg shadow-lg z-10 overflow-hidden">
                              <div className="max-h-40 overflow-y-auto">
                                {filterOptions[filter].map((option) => (
                                  <button
                                    key={option}
                                    onClick={() => selectFilterOption(filter, option)}
                                    className={`w-full px-4 py-2 text-left text-sm hover:bg-slate-50 transition-colors ${
                                      selectedFilters[filter] === option
                                        ? "bg-slate-100 text-slate-800 font-medium"
                                        : "text-slate-600"
                                    }`}
                                  >
                                    {option}
                                  </button>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Active Filters Display */}
                  {Object.values(selectedFilters).some(Boolean) && (
                    <div className="flex items-center gap-2 mt-3 pt-3 border-t border-slate-100">
                      <span className="text-xs text-slate-500">Active:</span>
                      {Object.entries(selectedFilters).map(
                        ([key, value]) =>
                          value && (
                            <span
                              key={key}
                              className="inline-flex items-center gap-1 px-2 py-1 bg-slate-100 text-slate-700 text-xs rounded-md"
                            >
                              {value}
                              <button
                                onClick={() => selectFilterOption(key, value)}
                                className="hover:text-slate-900"
                              >
                                ×
                              </button>
                            </span>
                          )
                      )}
                    </div>
                  )}
                </div>

                {/* Data Table */}
                <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
                  <table className="w-full">
                    <thead>
                      <tr className="bg-slate-50 border-b border-slate-200">
                        <th className="text-left px-6 py-4 text-sm font-semibold text-slate-700">
                          First Name
                        </th>
                        <th className="text-left px-6 py-4 text-sm font-semibold text-slate-700">
                          Last Name
                        </th>
                        <th className="text-left px-6 py-4 text-sm font-semibold text-slate-700">
                          Case Number
                        </th>
                        <th className="text-left px-6 py-4 text-sm font-semibold text-slate-700">
                          Status
                        </th>
                        <th className="text-left px-6 py-4 text-sm font-semibold text-slate-700">
                          Actions
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredCases.map((caseItem, index) => (
                        <tr
                          key={caseItem.id}
                          className={`border-b border-slate-100 hover:bg-slate-50 transition-colors ${
                            index % 2 === 0 ? "bg-white" : "bg-slate-50/50"
                          }`}
                        >
                          <td className="px-6 py-4 text-sm text-slate-600">{caseItem.firstName}</td>
                          <td className="px-6 py-4 text-sm text-slate-600">{caseItem.lastName}</td>
                          <td className="px-6 py-4 text-sm text-slate-800 font-medium">
                            {caseItem.caseNumber}
                          </td>
                          <td className="px-6 py-4">
                            <span className={`text-xs px-2 py-1 rounded-full font-medium ${getStatusColor(caseItem.status)}`}>
                              {caseItem.status}
                            </span>
                          </td>
                          <td className="px-6 py-4">
                            <button 
                              onClick={() => setSelectedCase(caseItem)}
                              className="text-slate-600 hover:text-slate-800 transition-colors"
                            >
                              <Eye className="w-5 h-5" />
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Register Button */}
                <div className="flex justify-end mt-6">
                  <button 
                    onClick={() => setShowRegisterModal(true)}
                    className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-white px-6 py-3 rounded-lg font-medium shadow-sm transition-all hover:shadow-md"
                  >
                    <Plus className="w-5 h-5" />
                    Register New Case
                  </button>
                </div>
              </>
            )}

            {/* My Cases View */}
            {currentView === "myCases" && (
              <>
                <h2 className="text-2xl font-semibold text-slate-800 mb-6">My Cases</h2>
                
                <div className="grid gap-4">
                  {cases.map((caseItem) => (
                    <div 
                      key={caseItem.id}
                      className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 hover:shadow-md transition-shadow"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <h3 className="text-lg font-semibold text-slate-800">
                              {caseItem.firstName} {caseItem.lastName}
                            </h3>
                            <span className={`text-xs px-2 py-1 rounded-full font-medium ${getStatusColor(caseItem.status)}`}>
                              {caseItem.status}
                            </span>
                          </div>
                          <div className="flex items-center gap-4 text-sm text-slate-500 mb-3">
                            <span className="flex items-center gap-1">
                              <FileText className="w-4 h-4" />
                              {caseItem.caseNumber}
                            </span>
                            <span className="flex items-center gap-1">
                              <Calendar className="w-4 h-4" />
                              {caseItem.dateOpened}
                            </span>
                            <span className="flex items-center gap-1">
                              <User className="w-4 h-4" />
                              {caseItem.assignedTo}
                            </span>
                          </div>
                          <p className="text-sm text-slate-600">{caseItem.description}</p>
                          <span className="inline-block mt-2 text-xs bg-slate-100 text-slate-600 px-2 py-1 rounded">
                            {caseItem.caseType}
                          </span>
                        </div>
                        <button 
                          onClick={() => setSelectedCase(caseItem)}
                          className="text-slate-600 hover:text-slate-800 p-2 hover:bg-slate-100 rounded-lg transition-colors"
                        >
                          <Eye className="w-5 h-5" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </>
            )}

            {/* Laws View */}
            {currentView === "laws" && (
              <>
                <h2 className="text-2xl font-semibold text-slate-800 mb-6">Laws Reference</h2>
                <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                  <p className="text-slate-600">Laws reference section coming soon...</p>
                </div>
              </>
            )}
          </div>
        </main>
      </div>

      {/* Register Case Modal */}
      {showRegisterModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-lg">
            <div className="flex items-center justify-between p-6 border-b border-slate-200">
              <h3 className="text-xl font-semibold text-slate-800">Register New Case</h3>
              <button 
                onClick={() => setShowRegisterModal(false)}
                className="text-slate-400 hover:text-slate-600 transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            <div className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    First Name *
                  </label>
                  <input
                    type="text"
                    value={formData.firstName}
                    onChange={(e) => setFormData({ ...formData, firstName: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-800"
                    placeholder="Enter first name"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    Last Name *
                  </label>
                  <input
                    type="text"
                    value={formData.lastName}
                    onChange={(e) => setFormData({ ...formData, lastName: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-800"
                    placeholder="Enter last name"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Case Type *
                </label>
                <select
                  value={formData.caseType}
                  onChange={(e) => setFormData({ ...formData, caseType: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-800"
                >
                  <option value="">Select case type</option>
                  {caseTypes.map((type) => (
                    <option key={type} value={type}>{type}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Assigned Judge
                </label>
                <select
                  value={formData.assignedTo}
                  onChange={(e) => setFormData({ ...formData, assignedTo: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-800"
                >
                  <option value="">Select judge</option>
                  {judges.map((judge) => (
                    <option key={judge} value={judge}>{judge}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Case Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-800 resize-none"
                  rows={3}
                  placeholder="Enter case details..."
                />
              </div>
            </div>
            <div className="flex justify-end gap-3 p-6 border-t border-slate-200">
              <button
                onClick={() => setShowRegisterModal(false)}
                className="px-4 py-2 text-slate-600 hover:text-slate-800 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleRegisterCase}
                className="px-6 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg font-medium transition-colors"
              >
                Register Case
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Case Detail Modal */}
      {selectedCase && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-lg">
            <div className="flex items-center justify-between p-6 border-b border-slate-200">
              <h3 className="text-xl font-semibold text-slate-800">Case Details</h3>
              <button 
                onClick={() => setSelectedCase(null)}
                className="text-slate-400 hover:text-slate-600 transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            <div className="p-6 space-y-4">
              <div className="flex items-center justify-between">
                <h4 className="text-lg font-semibold text-slate-800">
                  {selectedCase.firstName} {selectedCase.lastName}
                </h4>
                <span className={`text-xs px-2 py-1 rounded-full font-medium ${getStatusColor(selectedCase.status)}`}>
                  {selectedCase.status}
                </span>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-slate-500">Case Number</span>
                  <p className="font-medium text-slate-800">{selectedCase.caseNumber}</p>
                </div>
                <div>
                  <span className="text-slate-500">Case Type</span>
                  <p className="font-medium text-slate-800">{selectedCase.caseType}</p>
                </div>
                <div>
                  <span className="text-slate-500">Date Opened</span>
                  <p className="font-medium text-slate-800">{selectedCase.dateOpened}</p>
                </div>
                <div>
                  <span className="text-slate-500">Assigned To</span>
                  <p className="font-medium text-slate-800">{selectedCase.assignedTo}</p>
                </div>
              </div>
              <div>
                <span className="text-sm text-slate-500">Description</span>
                <p className="text-slate-800 mt-1">{selectedCase.description}</p>
              </div>
            </div>
            <div className="flex justify-end p-6 border-t border-slate-200">
              <button
                onClick={() => setSelectedCase(null)}
                className="px-6 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg font-medium transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
