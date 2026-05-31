import { useState, useEffect, useMemo, useCallback } from "react";
import NutritionCard from "./components/NutritionCard";
import { analyzeFoodSuitability } from "./components/Suitability";
import {
  Activity,
  Settings,
  UploadCloud,
  Loader2,
  Trash2,
  UserCircle,
  Moon,
  Sun,
  LayoutDashboard,
  X,
  ChevronRight,
} from "lucide-react";
function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [preview, setPreview] = useState(null);
  const [history, setHistory] = useState([]);
  const [selectedMeal, setSelectedMeal] = useState(null);

  // App Navigation & UI State
  const [activeTab, setActiveTab] = useState("analyze"); // 'analyze', 'log', 'settings'
  const [darkMode, setDarkMode] = useState(false);
  const [profile, setProfile] = useState("Healthy Adult");
  const [grams, setGrams] = useState(100);
  const [customGoal, setCustomGoal] = useState(2000);

  // Sync Profile Changes with active data
 const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Sync Profile Changes with active data
useEffect(() => {
  if (!data || !data.food_name) return;

  const reCalculateStatus = async () => {
    try {
      const response = await fetch(
        `${API_URL}/api/recalculate-status`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            food_name: data.food_name,
            nutrition: liveNutrition.nutrition,
            profile: profile,
          }),
        },
      );
      const result = await response.json();
      if (result.success) {
        setData((prev) => ({
          ...prev,
          warnings: result.warnings,
          risk_level: result.risk_level,
        }));
      }
    } catch (err) {
      console.error("Profile sync error:", err);
    }
  };
  reCalculateStatus();
}, [profile]);

  // Live Nutrition Scaling based on Portion Slider
  const liveNutrition = useMemo(() => {
    if (!data || !data.base_nutrition || !data.analyzed_grams) return null;

    // Calculate scaling factor
    const factor = grams / data.analyzed_grams;

    return {
      ...data,
      nutrition: {
        // Keep these as Numbers for easy calculations later
        calories: Math.round(data.base_nutrition.calories * factor),
        protein: Number((data.base_nutrition.protein * factor).toFixed(1)),
        carbs: Number((data.base_nutrition.carbs * factor).toFixed(1)),
        fat: Number((data.base_nutrition.fat * factor).toFixed(1)),
        gi: data.base_nutrition.gi,
        sodium: data.base_nutrition.sodium
          ? Number((data.base_nutrition.sodium * factor).toFixed(1))
          : 0,
        sugar: data.base_nutrition.sugar
          ? Number((data.base_nutrition.sugar * factor).toFixed(1))
          : 0,
        glycemicLoad:
          data.base_nutrition.gi && data.base_nutrition.carbs
            ? Number(
                (
                  (data.base_nutrition.gi *
                    (data.base_nutrition.carbs * factor)) /
                  100
                ).toFixed(1),
              )
            : 0,
        sat_fat: data.base_nutrition.sat_fat
          ? Number((data.base_nutrition.sat_fat * factor).toFixed(1))
          : 0,
      },
    };
  }, [data, grams]);

  // Handle adding food to local history
  const addFoodToLog = useCallback(() => {
    if (!liveNutrition) return;
    const newEntry = {
      id: Date.now(),
      name: liveNutrition.food_name,
      calories: liveNutrition.nutrition.calories,
      protein: liveNutrition.nutrition.protein, // Added
      carbs: liveNutrition.nutrition.carbs, // Added
      fat: liveNutrition.nutrition.fat, // Added
      gi: liveNutrition.nutrition.gi, // Added
      profile: profile,
      sodium: liveNutrition.nutrition.sodium, // Added
      sugar: liveNutrition.nutrition.sugar, // Added
      glycemicLoad: liveNutrition.nutrition.glycemicLoad, // Added
      sat_fat: liveNutrition.nutrition.sat_fat, // Added
      time: new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
    };
    setHistory((prevHistory) => {
      const updated = [newEntry, ...prevHistory];
      localStorage.setItem("nutrilens_logs", JSON.stringify(updated));
      return updated;
    });

    setActiveTab("log");
  }, [liveNutrition, profile]);

  // Handle clearing all logs
  const clearLogs = () => {
    if (window.confirm("Are you sure you want to clear all meal logs?")) {
      setHistory([]);
      localStorage.removeItem("nutrilens_logs");
    }
  };

  const dailyTotals = useMemo(() => {
    return history.reduce(
      (acc, item) => ({
        calories: acc.calories + (Number(item.calories) || 0),
        protein: acc.protein + (parseFloat(item.protein) || 0),
        carbs: acc.carbs + (parseFloat(item.carbs) || 0),
        fat: acc.fat + (parseFloat(item.fat) || 0),
      }),
      { calories: 0, protein: 0, carbs: 0, fat: 0 },
    );
  }, [history]);


  const analysis = useMemo(() => {
    if (!liveNutrition) return { status: "AWAITING", warnings: [] };

    return analyzeFoodSuitability(
      liveNutrition.nutrition,
      grams, // The value from your slider
      profile, // The current health profile state
    );
  }, [liveNutrition, grams, profile]);

  const removeMeal = (id) => {
    setHistory((prev) => {
      const updated = prev.filter((item) => item.id !== id);
      // Update storage so the deletion persists on refresh
      localStorage.setItem("nutrilens_logs", JSON.stringify(updated));
      return updated;
    });
  };

  useEffect(() => {
    const savedHistory = localStorage.getItem("nutrilens_logs");
    const savedGoal = localStorage.getItem("nutrilens_goal");
    if (savedHistory) setHistory(JSON.parse(savedHistory));
    if (savedGoal) setCustomGoal(Number(savedGoal));
  }, []);

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setPreview(URL.createObjectURL(file));
    setLoading(true);
    setData(null);
    const formData = new FormData();
    formData.append("file", file);
    formData.append("grams", grams);
    formData.append("health_profile", profile);
    try {
      const response = await fetch(`${API_URL}/api/analyze-image`, {
        method: "POST",
        body: formData,
      });
      const result = await response.json();
      if (result.success) {
        setData({
          ...result.data,
          base_nutrition: result.data.nutrition,
          analyzed_grams: grams,
        });
      }
    } catch (err) {
      console.error("Analysis Error:", err);
    } finally {
      setLoading(false);
    }
  };

  const totalCalories = history.reduce((sum, item) => sum + item.calories, 0);
  const calorieDiff = customGoal - totalCalories;
  const isOverLimit = totalCalories > customGoal;

    const getSmartMessage = useMemo(() => {
  // 1. Check for empty history first
  if (history.length === 0) {
    return "Upload a meal to see your personalized nutrition analysis!";
  }

  // 2. Setup Variables
  const totalCalories = dailyTotals.calories;
  const calorieDiff = customGoal - totalCalories;
  const isOverLimit = totalCalories > customGoal;
  const { protein, carbs, fat } = dailyTotals;

  // 3. PRIORITY 1: Calorie Limit Check
  if (isOverLimit) {
    return `Daily Limit Exceeded: You've crossed your goal by ${Math.abs(calorieDiff)} kcal. Consider focusing on hydration and light movement for the rest of the day.`;
  }

  if (calorieDiff < 200) {
    return `Budget Alert: You have only ${calorieDiff} kcal left. Aim for a light, high-protein snack if you're still hungry.`;
  }

  // 4. PRIORITY 2: Profile-Specific Macro Advice
  // Matching your profile strings (ensure these match your state exactly)
  if (profile === "Gym / Muscle Gain" && protein < 60) {
    return "Protein Alert: You're a bit low on protein for muscle synthesis. Your next choice should be lean protein like Greek yogurt or chicken.";
  }

  if (profile === "Type 2 Diabetes" && carbs > 150) {
    return "Carb Management: Your intake is high today. Focus on non-starchy vegetables and lean proteins to keep blood sugar stable.";
  }

  if (profile === "Hypertension (High BP)" && fat > 70) {
    return "Heart Health: Your fat intake is high today. Try to keep your next meal light on oils and saturated fats.";
  }

  // 5. PRIORITY 3: General Macro Warnings
  if (carbs > 200) {
    return "Balance Tip: Your carb intake is high. To stabilize energy levels, consider a fiber-rich snack or lean protein next.";
  }

  if (fat > 80) {
    return "Fat Intake: You've had a significant amount of fats today. Keep your next meal lean and focus on greens.";
  }

  // 6. DEFAULT: All good
  return "Your macros are looking perfectly balanced for your current profile. Keep up the great work!";
}, [dailyTotals, profile, history, customGoal]);

  return (
    <div className="bg-[#F8FAFC] text-slate-900 min-h-screen flex font-sans">
      {/* Sidebar Navigation */}
      <nav className="bg-white border-slate-200 w-20 lg:w-64 border-r flex flex-col p-6">
        <div className="flex items-center gap-3 px-2 mb-10">
          <div className="bg-blue-600 p-2 rounded-lg text-white">
            <Activity size={24} />
          </div>
          <span className="hidden lg:block font-bold text-xl tracking-tight">
            NutriLens AI
          </span>
        </div>

        <div className="flex flex-col gap-2 w-full flex-1">
          <NavItem
            icon={<LayoutDashboard size={20} />}
            label="Analyze"
            active={activeTab === "analyze"}
            onClick={() => setActiveTab("analyze")}
          />
          <NavItem
            icon={<Activity size={20} />}
            label="Meal Log"
            active={activeTab === "log"}
            onClick={() => setActiveTab("log")}
          />

          <div className="hidden lg:block mt-8">
            <div className="mb-6 px-2">
              <div className="flex justify-between items-end mb-2">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                  Daily Progress
                </span>
                <span className="text-xs font-bold">
                  {dailyTotals.calories} / {customGoal}
                </span>
              </div>
              <div className="bg-slate-100 h-1.5 w-full rounded-full overflow-hidden shadow-inner">
                <div
                  className={`h-full transition-all duration-1000 ${dailyTotals.calories > customGoal ? "bg-rose-500" : "bg-blue-600"}`}
                  style={{
                    width: `${Math.min((dailyTotals.calories / customGoal) * 100, 100)}%`,
                  }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Separator Line and Pinned Settings */}
        <div className="mt-auto pt-4">
          <hr className="mb-4 border-slate-200" />
          <NavItem
            icon={<Settings size={20} />}
            label="Settings"
            active={activeTab === "settings"}
            onClick={() => setActiveTab("settings")}
          />
        </div>
      </nav>

      <main className="flex-1 p-6 lg:p-10 overflow-y-auto">
        {/* VIEW ROUTING */}

        {/* --- SETTINGS VIEW --- */}
        {activeTab === "settings" && (
          <div className="max-w-2xl mx-auto space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <header>
              <h1 className="text-4xl font-black tracking-tight">Settings</h1>
              <p className="text-slate-500">Configure your preferences.</p>
            </header>
            <section className="bg-white border-slate-200 p-8 rounded-3xl border space-y-8 shadow-sm">
              <div className="space-y-4">
                <h4 className="font-bold text-lg">Daily Calorie Goal</h4>
                <p className="text-sm text-slate-500 mb-2">
                  Set your target caloric intake for the day.
                </p>
                <input
                  type="number"
                  value={customGoal}
                  onChange={(e) => {
                    setCustomGoal(e.target.value);
                    localStorage.setItem("nutrilens_goal", e.target.value);
                  }}
                  className="bg-slate-50 border-slate-200 w-full p-4 rounded-2xl border font-bold text-xl focus:ring-2 ring-blue-500 outline-none"
                />
              </div>
            </section>
          </div>
        )}

        {/* --- MEAL LOG VIEW --- */}
{activeTab === "log" && (
  <div className="max-w-4xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-500">
    <header className="mb-10 flex justify-between items-center">
      <div>
        <h1 className="text-4xl font-black tracking-tight text-slate-900">
          Daily Food Log
        </h1>
        <p className="text-slate-500 font-medium">
          Review your nutrition for the day.
        </p>
      </div>
      <button
        onClick={clearLogs}
        className="flex items-center gap-2 px-4 py-2 bg-rose-50 text-rose-600 rounded-xl font-bold text-sm"
      >
        <Trash2 size={18} /> Clear
      </button>
    </header>

    {/* Smart Analysis Card with dynamic background */}
    <div className={`rounded-[2.5rem] p-8 mb-8 text-white shadow-xl relative overflow-hidden transition-all duration-500 ${
      isOverLimit 
        ? "bg-gradient-to-br from-rose-600 to-rose-700" 
        : "bg-gradient-to-br from-blue-600 to-indigo-700"
    }`}>
      {/* Decorative background icon */}
      <div className="absolute -right-6 -bottom-6 opacity-10 rotate-12">
        <Activity size={140} />
      </div>

      <div className="relative z-10">
        <div className="flex items-center gap-2 mb-4">
          <div className="bg-white/20 p-2 rounded-xl backdrop-blur-md">
            <Activity size={20} className="text-white" />
          </div>
          <span className="text-[10px] font-black uppercase tracking-[0.2em] opacity-90">
            NutriLens Coach
          </span>
        </div>

        <h3 className="text-2xl font-black mb-2">Smart Analysis</h3>
        <p className="text-blue-50 text-lg leading-relaxed font-medium italic">
          "{getSmartMessage}"
        </p>
      </div>
    </div>

            {/* TOTAL MACROS SUMMARY BAR */}
            <div className="bg-white border border-slate-200 rounded-[2.5rem] p-8 mb-8 shadow-sm grid grid-cols-2 md:grid-cols-4 gap-6">
              <div className="text-center">
                <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">
                  Calories
                </p>
                <p className="text-2xl font-black text-blue-600">
                  {dailyTotals.calories}
                  <span className="text-xs ml-0.5 opacity-70">kcal</span>
                </p>
              </div>
              <div className="text-center">
                <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">
                  Protein
                </p>
                <p className="text-2xl font-black text-emerald-600">
                  {dailyTotals.protein.toFixed(1)}
                  <span className="text-xs ml-0.5 opacity-70">g</span>
                </p>
              </div>
              <div className="text-center">
                <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">
                  Carbs
                </p>
                <p className="text-2xl font-black text-amber-600">
                  {dailyTotals.carbs.toFixed(1)}
                  <span className="text-xs ml-0.5 opacity-70">g</span>
                </p>
              </div>
              <div className="text-center">
                <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">
                  Fat
                </p>
                <p className="text-2xl font-black text-rose-600">
                  {dailyTotals.fat.toFixed(1)}
                  <span className="text-xs ml-0.5 opacity-70">g</span>
                </p>
              </div>
            </div>

            {/* MEAL LIST (CLICKABLE) */}
            <div className="space-y-3">
              {history.map((item) => (
                /* We use 'group' here so the bin icon shows up on hover */
                <div
                  key={item.id}
                  className="relative group flex items-center gap-3"
                >
                  {/* MAIN MEAL BUTTON */}
                  <button
                    onClick={() => setSelectedMeal(item)}
                    className="flex-1 flex justify-between items-center p-6 bg-white border border-slate-200 rounded-[1.5rem] shadow-sm hover:border-blue-400 transition-all text-left"
                  >
                    <div className="flex items-center gap-5">
                      <div className="bg-slate-50 p-4 rounded-2xl">
                        <Activity className="text-blue-600" size={24} />
                      </div>
                      <div>
                        <h4 className="font-bold text-xl capitalize text-slate-900">
                          {item.name.replace(/_/g, " ")}
                        </h4>
                        <p className="text-xs font-bold text-slate-400 uppercase tracking-wide">
                          {item.time} • {item.profile}
                        </p>
                      </div>
                    </div>

                    <div className="text-right flex items-center gap-4">
                      <div>
                        <span className="text-2xl font-black text-slate-900">
                          {item.calories}
                        </span>
                        <span className="text-xs font-bold text-slate-400 ml-1 uppercase">
                          kcal
                        </span>
                      </div>
                      <ChevronRight
                        className="text-slate-300 group-hover:text-blue-600 transition-colors"
                        size={20}
                      />
                    </div>
                  </button>

                  {/* DELETE BIN BUTTON */}
                  <button
                    onClick={(e) => {
                      e.stopPropagation(); 
                      removeMeal(item.id);
                    }}
                    className="p-4 text-slate-300 hover:text-rose-500 hover:bg-rose-50 rounded-2xl transition-all opacity-0 group-hover:opacity-100"
                    title="Delete entry"
                  >
                    <Trash2 size={22} />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
        {/* --- ANALYZE VIEW --- */}
        {activeTab === "analyze" && (
          <div className="animate-in fade-in duration-500">
            <header className="mb-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
              <div>
                <h1 className="text-4xl font-black tracking-tight">
                  Intelligence Dashboard
                </h1>
                <p className="text-slate-500 font-medium italic">
                  Adjust portion size then capture your meal
                </p>
              </div>
              <div className="bg-white border-slate-200 flex items-center gap-3 p-2 pl-4 rounded-2xl border shadow-sm">
                <div className="flex flex-col items-end">
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                    Health Profile
                  </span>
                  <select
                    value={profile}
                    onChange={(e) => setProfile(e.target.value)}
                    className="text-sm font-bold bg-transparent focus:outline-none cursor-pointer"
                  >
                    <option value="Healthy Adult">Healthy Adult</option>
                    <option value="Type 2 Diabetes">Type 2 Diabetes</option>
                    <option value="Hypertension (High BP)">
                      Hypertension (High BP)
                    </option>
                    <option value="Weight Loss / Obesity">
                      Weight Loss / Obesity
                    </option>
                    <option value="Gym / Muscle Gain">Gym / Muscle Gain</option>
                  </select>
                </div>
                <div className="w-10 h-10 rounded-xl flex items-center justify-center text-slate-300 border border-slate-200">
                  <UserCircle size={24} />
                </div>
              </div>
            </header>

            <div className="grid grid-cols-1 xl:grid-cols-12 gap-8 items-start">
              <div className="xl:col-span-5 space-y-6">
                {/* Portion Slider Section */}
                <section className="bg-white border-slate-200 p-6 rounded-[2rem] border shadow-sm">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="font-bold text-sm uppercase tracking-widest text-slate-400">
                      Portion Size
                    </h3>
                    <span className="bg-blue-600 text-white px-3 py-1 rounded-lg font-black text-sm">
                      {grams}g
                    </span>
                  </div>
                  <input
                    type="range"
                    min="50"
                    max="1000"
                    step="10"
                    value={grams}
                    onChange={(e) => setGrams(e.target.value)}
                    className="w-full h-1.5 bg-blue-100 rounded-lg appearance-none cursor-pointer accent-blue-600"
                  />
                  <div className="flex justify-between mt-2 text-[10px] font-bold text-slate-400 uppercase tracking-tighter">
                    <span>Snack (50g)</span>
                    <span>Meal (1kg)</span>
                  </div>
                </section>

                {/* Capture Meal Card */}
                <section className="bg-white border-slate-200 p-8 rounded-[2rem] border shadow-sm">
                  <div className="flex justify-between items-center mb-6">
                    <h3 className="font-bold text-lg tracking-tight">
                      Capture Meal
                    </h3>
                    {preview && (
                      <button
                        onClick={() => {
                          setPreview(null);
                          setData(null);
                        }}
                        className="text-xs font-bold text-rose-500 hover:underline"
                      >
                        Clear
                      </button>
                    )}
                  </div>

                  <label className="hover:bg-blue-50/30 border-slate-200 group relative flex flex-col items-center justify-center w-full min-h-[380px] border-2 border-dashed rounded-[2rem] cursor-pointer transition-all overflow-hidden bg-transparent">
                    {preview ? (
                      <img
                        src={preview}
                        alt="Preview"
                        className="absolute inset-0 w-full h-full object-cover"
                      />
                    ) : (
                      <div className="flex flex-col items-center justify-center p-6 text-center">
                        <div className="bg-blue-50 text-blue-600 p-5 rounded-2xl mb-5 group-hover:scale-110 transition-transform">
                          <UploadCloud size={32} />
                        </div>
                        <p className="text-lg font-bold text-slate-700">
                          Drop your food photo here
                        </p>
                        <p className="text-sm text-slate-400 mt-2">
                          Supports JPG, PNG from gallery or camera
                        </p>
                      </div>
                    )}
                    <input
                      type="file"
                      className="hidden"
                      onChange={handleFileUpload}
                    />
                  </label>
                </section>
              </div>

              {/* Analysis Result Area */}
              <div className="xl:col-span-7">
                {loading ? (
                  <div className="bg-white border-slate-200 p-20 rounded-[2rem] border shadow-sm flex flex-col items-center justify-center min-h-[480px]">
                    <Loader2
                      className="animate-spin text-blue-600 mb-4"
                      size={48}
                    />
                    <h3 className="text-xl font-bold">
                      Extracting Nutrients...
                    </h3>
                  </div>
                ) : liveNutrition ? (
                  <NutritionCard
                    data={liveNutrition}
                    onAddToLog={addFoodToLog}
                    profile={profile}
                    analysis={analysis}
                  />
                ) : (
                  <EmptyState />
                )}
              </div>
            </div>
          </div>
        )}
      </main>
      {/* MEAL INSPECTOR MODAL */}
      {selectedMeal && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-in fade-in duration-200">
          <div
            className={`${typeof darkMode !== "undefined" && darkMode ? "bg-[#1E293B] text-white" : "bg-white text-slate-900"} w-full max-w-md rounded-[2.5rem] shadow-2xl overflow-hidden animate-in zoom-in-95 duration-200`}
          >
            <div className="p-8 border-b border-slate-100 dark:border-slate-700 flex justify-between items-center bg-slate-50/50">
              <div>
                <h3 className="font-black text-2xl capitalize">
                  {(selectedMeal.name || "Unknown Meal").replace(/_/g, " ")}
                </h3>
                <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">
                  {selectedMeal.time || "N/A"} Analysis
                </p>
              </div>
              <button
                onClick={() => setSelectedMeal(null)}
                className="p-3 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-full hover:scale-110 transition-transform shadow-sm"
              >
                <X size={20} className="text-slate-500" />
              </button>
            </div>

            <div className="p-8 space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <DetailBox
                  label="Protein"
                  value={selectedMeal.protein || 0}
                  unit="g"
                  color="text-emerald-500"
                  darkMode={typeof darkMode !== "undefined" ? darkMode : false}
                />
                <DetailBox
                  label="Carbs"
                  value={selectedMeal.carbs || 0}
                  unit="g"
                  color="text-amber-500"
                  darkMode={typeof darkMode !== "undefined" ? darkMode : false}
                />
                <DetailBox
                  label="Fat"
                  value={selectedMeal.fat || 0}
                  unit="g"
                  color="text-rose-500"
                  darkMode={typeof darkMode !== "undefined" ? darkMode : false}
                />
                <DetailBox
                  label="GI Index"
                  value={selectedMeal.gi || "N/A"}
                  unit=""
                  color="text-purple-500"
                  darkMode={typeof darkMode !== "undefined" ? darkMode : false}
                />
              </div>

              <button
                onClick={() => setSelectedMeal(null)}
                className="w-full py-4 bg-blue-600 text-white font-black rounded-2xl shadow-lg shadow-blue-500/30 hover:bg-blue-700 transition-all active:scale-95"
              >
                {" "}
                Close Details{" "}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

const NavItem = ({ icon, label, active, onClick }) => (
  <button
    onClick={onClick}
    className={`flex items-center gap-4 w-full p-3.5 rounded-xl transition-all ${
      active
        ? "bg-blue-600 text-white shadow-lg shadow-blue-500/20"
        : "text-slate-500 hover:bg-slate-50"
    }`}
  >
    {icon}
    <span className="hidden lg:block font-bold text-sm tracking-wide">
      {label}
    </span>
  </button>
);

const EmptyState = () => (
  <div className="bg-white border-slate-200 h-full min-h-[480px] border-2 border-dashed rounded-[2rem] flex flex-col items-center justify-center text-center p-12 shadow-sm">
    <div className="bg-blue-50 p-6 rounded-3xl mb-6">
      <Activity size={48} className="text-blue-500 opacity-80" />
    </div>
    <h3 className="text-2xl font-bold mb-3 tracking-tight">Awaiting Capture</h3>
    <p className="text-slate-500 max-w-xs mx-auto text-sm leading-relaxed mb-10">
      Select your portion size and upload a photo. AI will cross-verify with
      your health profile.
    </p>
    <div className="flex gap-3 justify-center">
      <div className="bg-slate-50 border-slate-100 px-5 py-2.5 rounded-xl text-[10px] font-bold text-slate-400 uppercase border tracking-[0.1em] shadow-sm">
        EfficientNet-B0
      </div>
      <div className="bg-slate-50 border-slate-100 px-5 py-2.5 rounded-xl text-[10px] font-bold text-slate-400 uppercase border tracking-[0.1em] shadow-sm">
        USDA DB
      </div>
    </div>
  </div>
);

const DetailBox = ({ label, value, unit, color, darkMode }) => (
  <div
    className={`${darkMode ? "bg-slate-800 border-slate-700" : "bg-slate-50 border-slate-100"} p-5 border rounded-3xl`}
  >
    <p
      className={`text-[10px] font-black uppercase tracking-widest mb-1 ${color}`}
    >
      {label}
    </p>
    <p className="text-2xl font-black">
      {value}
      <span className="text-xs ml-1 opacity-40 font-bold">{unit}</span>
    </p>
  </div>
);
export default App;
