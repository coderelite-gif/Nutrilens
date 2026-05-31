// Inside src/components/ImageUploader.jsx
export default function ImageUploader({ setResult, setLoading }) {
  
  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setLoading(true);

    // Prepare the data to send to FastAPI
    const formData = new FormData();
    formData.append("file", file);
    formData.append("grams", 100); 
    formData.append("health_profile", "Healthy Adult");

    try {
      // Make the call to your FastAPI server
      const response = await fetch("http://localhost:8000/api/analyze-image", {
        method: "POST",
        body: formData,
      });
      
      const data = await response.json();
      if (data.success) {
        setResult(data.data); // Update the UI with the result
      }
    } catch (error) {
      console.error("Error analyzing image:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="border-2 border-dashed border-gray-300 rounded-lg p-10 text-center hover:bg-gray-50 transition-colors">
      <input 
        type="file" 
        accept="image/*" 
        onChange={handleFileUpload} 
        className="hidden" 
        id="file-upload" 
      />
      <label htmlFor="file-upload" className="cursor-pointer">
        <span className="text-blue-600 font-semibold">Click to upload</span> or drag and drop
      </label>
    </div>
  );
}