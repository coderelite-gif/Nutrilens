import React from "react";
import {
  ShieldAlert,
  Leaf,
  PlusCircle,
  CheckCircle2,
  AlertTriangle,
} from "lucide-react";

const NutritionCard = ({ data, onAddToLog, profile, analysis }) => {
  if (!data) return null;

  const { food_name, confidence, nutrition, alternatives, top_matches } = data;

  const getRiskLevel = () => {
    if (analysis?.status === "UNSUITABLE") return "high";
    if (analysis?.status === "CAUTION") return "moderate";
    return "low";
  };

  const risk_level = getRiskLevel();

  const riskConfig = {
    low: {
      color: "bg-emerald-500",
      text: "text-emerald-700",
      bg: "bg-emerald-50",
      label: "Suitable",
    },
    moderate: {
      color: "bg-amber-500",
      text: "text-amber-700",
      bg: "bg-amber-50",
      label: "Caution Required",
    },
    high: {
      color: "bg-rose-500",
      text: "text-rose-700",
      bg: "bg-rose-50",
      label: "Unsuitable / High Risk",
    },
  };

  const currentRisk = riskConfig[risk_level] || riskConfig.low;

  const displayConfidence =
    confidence <= 1 ? Math.round(confidence * 100) : Math.round(confidence);

  return (
    <div className="bg-white rounded-[2rem] shadow-xl border border-slate-200 overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-500">
      {/* Dynamic Status Bar - Reacts to Portion Analysis */}
      <div
        className={`h-3 w-full ${currentRisk.color} transition-colors duration-500`}
      />

      <div className="p-8 border-b border-slate-100">
        <div className="flex justify-between items-start gap-4">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-3">
              <span
                className={`${currentRisk.bg} ${currentRisk.text} px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest flex items-center gap-1.5 border border-current opacity-80`}
              >
                {risk_level === "high" ? (
                  <ShieldAlert size={12} />
                ) : (
                  <CheckCircle2 size={12} />
                )}
                {analysis?.status || currentRisk.label} for{" "}
                {profile?.replace(/_/g, " ")}
              </span>
            </div>
            <h2 className="text-4xl font-black text-slate-900 capitalize tracking-tight mb-2">
              {food_name.replace(/_/g, " ")}
            </h2>

            <div className="flex flex-wrap gap-2 mt-4">
              <span className="text-[10px] font-bold text-slate-400 uppercase self-center mr-1">
                Detection:
              </span>
              {top_matches?.map((match, i) => (
                <div
                  key={i}
                  className="bg-slate-50 px-2 py-1 rounded-md border border-slate-100 flex gap-2 items-center"
                >
                  <span className="text-[10px] font-bold text-slate-600 capitalize">
                    {match.food}
                  </span>
                  <span className="text-[10px] font-medium text-slate-400">
                    {Math.round(
                      match.confidence > 1
                        ? match.confidence
                        : match.confidence * 100,
                    )}
                    %
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="text-right shrink-0">
            <div className="inline-flex flex-col items-end">
              <p className="text-3xl font-black text-slate-900 leading-none">
                {displayConfidence}%
              </p>
              <p className="text-[10px] font-bold text-slate-400 uppercase tracking-tighter mt-1">
                AI Accuracy
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="p-8 space-y-8">
        {/* Macro Grid */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <MacroTile
            label="Calories"
            value={nutrition.calories}
            unit="kcal"
            color="bg-orange-500"
          />
          <MacroTile
            label="Protein"
            value={nutrition.protein}
            unit="g"
            color="bg-emerald-500"
          />
          <MacroTile
            label="Carbs"
            value={nutrition.carbs}
            unit="g"
            color="bg-blue-500"
          />
          <MacroTile
            label="Fat"
            value={nutrition.fat}
            unit="g"
            color="bg-rose-500"
          />
          <MacroTile
            label="GI Index"
            value={nutrition.gi || "N/A"}
            unit=""
            color="bg-purple-500"
          />
        </div>

        {/* Updated Health Analysis Section */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div
            className={`${currentRisk.bg} border border-slate-200 p-6 rounded-2xl transition-colors duration-500`}
          >
            <h4
              className={`flex items-center gap-2 ${currentRisk.text} font-black text-xs uppercase tracking-widest mb-4`}
            >
              <AlertTriangle size={16} /> Portion Analysis
            </h4>

            {/* Logic: Priority given to our local analysis warnings */}
            {analysis?.warnings.length > 0 ? (
              <ul className="space-y-3">
                {analysis.warnings.map((w, i) => (
                  <li
                    key={i}
                    className="text-xs text-slate-700 flex items-start gap-2 leading-relaxed font-bold"
                  >
                    <div
                      className={`w-1.5 h-1.5 rounded-full mt-1.5 shrink-0 ${currentRisk.color}`}
                    />
                    {w}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-xs text-emerald-600 font-bold flex items-center gap-2">
                <CheckCircle2 size={14} /> This portion is safe for your
                profile.
              </p>
            )}
          </div>

          <div className="bg-slate-50 border border-slate-200 p-6 rounded-2xl">
            <h4 className="flex items-center gap-2 text-slate-700 font-black text-xs uppercase tracking-widest mb-4">
              <Leaf size={16} className="text-emerald-600" /> Suggested Swaps
            </h4>
            <div className="flex flex-col gap-2">
              {/* Use analysis.alternatives if available, otherwise fallback to data.alternatives */}
              {(analysis?.alternatives?.length > 0
                ? analysis.alternatives
                : data.alternatives
              ).map((alt, i) => (
                <div
                  key={i}
                  className="bg-white text-slate-700 px-4 py-3 rounded-xl text-[11px] font-bold border border-slate-100 shadow-sm flex justify-between items-center"
                >
                  {alt}
                  <PlusCircle size={14} className="text-emerald-500" />
                </div>
              ))}
            </div>
          </div>
        </div>

        <button
          onClick={onAddToLog}
          className="w-full flex items-center justify-center gap-3 bg-blue-600 hover:bg-blue-700 text-white font-black uppercase tracking-widest py-5 rounded-2xl transition-all active:scale-[0.98] shadow-lg shadow-blue-200"
        >
          <PlusCircle size={20} />
          Add to Daily Food Log
        </button>
      </div>
    </div>
  );
};

const MacroTile = ({ label, value, unit, color }) => (
  <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100 flex flex-col justify-between min-h-[100px] transition-all hover:border-slate-300 shadow-sm">
    <div>
      <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">
        {label}
      </p>
      <p className="text-2xl font-black text-slate-800 leading-none">
        {value}
        <span className="text-[10px] ml-1 font-bold uppercase text-slate-400">
          {unit}
        </span>
      </p>
    </div>
    <div className={`h-1 w-full ${color} rounded-full mt-4 opacity-30`} />
  </div>
);

export default NutritionCard;
