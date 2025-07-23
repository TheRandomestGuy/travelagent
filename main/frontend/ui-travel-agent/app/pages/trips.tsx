import { useSession } from 'next-auth/react';
import { useRouter } from 'next/router';
import { useState } from 'react';

export default function Trips() {
  const { data: session } = useSession();
  const router = useRouter();
  const [trips, setTrips] = useState<string[]>(['Trip to Paris', 'Beach in Bali']);

  const handleAddTrip = () => {
    router.push('/plan');
  };

  if (!session) return <p>Please sign in to view your trips.</p>;

  return (
    <div className="max-w-2xl mx-auto mt-10">
      <h2 className="text-2xl mb-4">Your Trips</h2>
      <ul className="mb-4">
        {trips.map((trip, i) => (
          <li key={i} className="border p-2 mb-2">{trip}</li>
        ))}
      </ul>
      <button onClick={handleAddTrip} className="bg-green-500 text-white px-4 py-2 rounded">
        + Add New Trip
      </button>
    </div>
  );
}