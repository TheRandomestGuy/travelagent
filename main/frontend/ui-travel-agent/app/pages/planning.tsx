import { useState } from 'react';

export default function Plan() {
  const [form, setForm] = useState({
    destination: '',
    startDate: '',
    endDate: '',
    goals: '',
  });
  const [result, setResult] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async () => {
    const res = await fetch('http://localhost:8000/plan-trip', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form),
    });
    const data = await res.json();
    setResult(data.response);
  };

  return (
    <div className="max-w-xl mx-auto mt-10">
      <h2 className="text-2xl mb-4">Plan a New Trip</h2>
      <input
        name="destination"
        placeholder="Destination"
        value={form.destination}
        onChange={handleChange}
        className="w-full border p-2 mb-2"
      />
      <input
        name="startDate"
        type="date"
        value={form.startDate}
        onChange={handleChange}
        className="w-full border p-2 mb-2"
      />
      <input
        name="endDate"
        type="date"
        value={form.endDate}
        onChange={handleChange}
        className="w-full border p-2 mb-2"
      />
      <textarea
        name="goals"
        placeholder="What are your travel goals?"
        value={form.goals}
        onChange={handleChange}
        className="w-full border p-2 mb-2"
      />
      <button onClick={handleSubmit} className="bg-blue-600 text-white px-4 py-2 rounded">
        Plan Trip
      </button>

      {result && (
        <div className="mt-4 p-4 border bg-gray-50">
          <h3 className="text-lg font-semibold">Planned Itinerary:</h3>
          <p>{result}</p>
        </div>
      )}
    </div>
  );
}
