import { getProviders, signIn } from 'next-auth/react';
import { GetServerSideProps } from 'next';

export default function SignIn({ providers }: any) {
  return (
    <div className="flex flex-col items-center justify-center h-screen">
      <h1 className="text-3xl mb-4">Sign in to your account</h1>
      {Object.values(providers).map((provider: any) => (
        <button
          key={provider.name}
          onClick={() => signIn(provider.id)}
          className="bg-gray-800 text-white px-4 py-2 rounded mb-2"
        >
          Sign in with {provider.name}
        </button>
      ))}
    </div>
  );
}

export const getServerSideProps: GetServerSideProps = async () => {
  const providers = await getProviders();
  return {
    props: { providers },
  };
};