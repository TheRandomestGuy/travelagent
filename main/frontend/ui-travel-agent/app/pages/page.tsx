"use client";
import { useSession, signIn } from 'next-auth/react';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const { data: session, status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (session) router.push('/pages/trips');
  }, [session]);

  return (
    <div className="flex flex-col items-center justify-center h-screen">
      <h1 className="text-4xl mb-4">Welcome to AI Travel Planner</h1>
      <button
        onClick={() => signIn()}
        className="bg-blue-600 text-white px-4 py-2 rounded"
      >
        Sign In to Start Planning
      </button>
    </div>
  );
}