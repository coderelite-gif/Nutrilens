export const analyzeFoodSuitability = (nutrition, weight, profile) => {
  const warnings = [];
  const alternatives = [];
  let status = 'SUITABLE';
const {calories, protein, carbs, fat, sat_fat, gi, sugar, sodium, glycemicLoad} = nutrition;

  switch (profile) {
    case "Type 2 Diabetes":
      // Focus: Glycemic impact and total carb load
      if (glycemicLoad > 20 || sugar > 15) {
        status = 'UNSUITABLE';
        warnings.push(`High Glycemic Load: A GL of ${glycemicLoad} is excessive for blood sugar stability.`);
        alternatives.push("Greek Yogurt with Cinnamon", "Handful of Almonds", "Chia Seed Pudding");
      } 
      else if (glycemicLoad > 10 || gi > 55) {
        status = (status === 'UNSUITABLE') ? 'UNSUITABLE' : 'CAUTION';
        warnings.push("Moderate Glycemic Impact: Monitor for blood sugar spikes.");
      }
      
      if (carbs > 50) {
        warnings.push(`Carb Alert: ${carbs}g carbs exceeds the recommended 45g meal ceiling.`);

      }
      break;

    case "Hypertension (High BP)":
      // Focus: Sodium, Saturated Fat, and Volume
      if (sodium > 600 || (weight > 500 && sodium > 400)) {
        status = 'UNSUITABLE';
        warnings.push(`High Sodium: ${sodium}mg exceeds safe levels for blood pressure management.`);   
      }

       if(sodium > 600 || sat_fat > 5 || fat > 20 || (weight > 500 && sodium > 400)){ 
            alternatives.push("Lemon-Herb Quinoa", "Steamed Brown Rice", "Fresh Garden Salad");
      }
      
      if (sat_fat > 5 || fat > 20) {
        status = (status === 'UNSUITABLE') ? 'UNSUITABLE' : 'CAUTION';
        warnings.push("Lipid Warning: High saturated fats can impact arterial health.");
      }
      break;

    case "Weight Loss / Obesity":
      // Focus: Energy density and insulin triggers (sugar)
      if (calories > 600) {
        status = 'UNSUITABLE';
        warnings.push(`Calorie Surplus: ${calories}kcal is too high for a single weight-loss meal.`);
      } else if (calories > 400) {
        status = 'CAUTION';
        warnings.push("Portion Alert: Slightly exceeds ideal weight-loss calorie window.");
        alternatives.push("Cauliflower Rice Stir-fry", "Zucchini Noodles", "Grilled Chicken Breast");
      }

      if (sugar > 12) {
        warnings.push("Sugar Warning: High sugar intake can halt metabolic fat burning.");
      }
      break;

    case "Gym / Muscle Gain":
      // Focus: Protein to Calorie ratio
      if (protein < 20 && calories > 500) {
        status = 'CAUTION';
        warnings.push("Low Protein Density: Insufficient for optimal muscle protein synthesis.");
        lternatives.push("Add 150g Grilled Chicken", "Mix in a scoop of Whey","5 - 6 eggs");
      }
      
      if (calories > 900) {
        warnings.push("Calorie Excess: Monitor for unwanted fat gain during your bulk.");
      }
      break;

    case "Healthy Adult":
      if (calories > 800) {
        status = 'CAUTION';
        warnings.push("High Energy Intake: Consider balancing with a lighter meal later.");
      }
      if (sodium > 1000) {
        warnings.push("Sodium Warning: Approaching 50% of the daily recommended salt limit.");
      }
      break;

      default:
      alternatives.push("A smaller portion size", "Pair with a high-fiber salad");
  }

  return { status, warnings, alternatives };
};