"use client";
import Link from 'next/link';
import { useSession, signOut } from 'next-auth/react';

export default function Navbar() {
  const { data: session } = useSession();

  return (
    <nav className="bg-gray-800 text-white px-4 py-3 flex justify-between items-center">
      <div className="flex gap-4">
        <Link href="/pages">
          <span className="hover:underline cursor-pointer">Home</span>
        </Link>
        {session && (
          <>
            <Link href="/pages/trips">
              <span className="hover:underline cursor-pointer">Trips</span>
            </Link>
            <Link href="/pages/account">
              <span className="hover:underline cursor-pointer">Account</span>
            </Link>
            <Link href="/pages/plan">
              <span className="hover:underline cursor-pointer">Plan</span>
            </Link>
          </>
        )}
      </div>
      <div>
        {session && (
          <button onClick={() => signOut()} className="hover:underline">
            Sign Out
          </button>
        )}
      </div>
    </nav>
  );
}