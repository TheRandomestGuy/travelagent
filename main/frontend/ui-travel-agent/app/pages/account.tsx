import { useSession } from 'next-auth/react';
import { useState } from 'react';

export default function Account() {
  const { data: session } = useSession();
  const [form, setForm] = useState({
    interests: '',
    hotelPreference: '',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSave = () => {
    console.log('Saving user preferences:', form);
  };

  if (!session) return <p>Please sign in to access this page.</p>;

  return (
    <div className="max-w-xl mx-auto mt-10">
      <h2 className="text-2xl mb-4">Your Travel Preferences</h2>
      <input
        name="interests"
        placeholder="Interests (e.g. beaches, hiking)"
        value={form.interests}
        onChange={handleChange}
        className="w-full border p-2 mb-4"
      />
      <input
        name="hotelPreference"
        placeholder="Hotel Preference (e.g. luxury, budget)"
        value={form.hotelPreference}
        onChange={handleChange}
        className="w-full border p-2 mb-4"
      />
      <button onClick={handleSave} className="bg-blue-500 text-white px-4 py-2 rounded">
        Save Preferences
      </button>
    </div>
  );
}