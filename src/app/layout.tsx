import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "AnyGame - Play Online Games For Free",
  description: "AnyGame is a free online game platform with thousands of games to play. Browse our categories and enjoy the best gaming experience.",
  keywords: "online games, free games, browser games, html5 games, game platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh">
      <body className={inter.className}>
        <div className="min-h-screen flex flex-col">
          <header className="bg-gray-800 text-white shadow-md">
            <div className="container mx-auto px-4 py-4 flex justify-between items-center">
              <h1 className="text-2xl font-bold">AnyGame</h1>
              <nav>
                <ul className="flex space-x-4">
                  <li><a href="/" className="hover:text-blue-300 transition-colors">首页</a></li>
                  <li><a href="/categories" className="hover:text-blue-300 transition-colors">分类</a></li>
                  <li><a href="/popular" className="hover:text-blue-300 transition-colors">热门</a></li>
                </ul>
              </nav>
            </div>
          </header>
          <main className="flex-grow container mx-auto px-4 py-8">
        {children}
          </main>
          <footer className="bg-gray-800 text-white">
            <div className="container mx-auto px-4 py-6">
              <p className="text-center">&copy; {new Date().getFullYear()} AnyGame - 所有游戏版权归原作者所有</p>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
