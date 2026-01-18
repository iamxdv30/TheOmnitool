"use client";

import Link from "next/link";
import { Github, Twitter, Mail } from "lucide-react";

const footerLinks = [
  {
    title: "Product",
    links: [
      { href: "/tools", label: "Tools" },
      { href: "/pricing", label: "Pricing" },
      { href: "/docs", label: "Documentation" },
    ],
  },
  {
    title: "Company",
    links: [
      { href: "/about", label: "About" },
      { href: "/contact", label: "Contact" },
      { href: "/blog", label: "Blog" },
    ],
  },
  {
    title: "Legal",
    links: [
      { href: "/privacy", label: "Privacy" },
      { href: "/terms", label: "Terms" },
    ],
  },
];

const socialLinks = [
  { href: "https://github.com", icon: Github, label: "GitHub" },
  { href: "https://twitter.com", icon: Twitter, label: "Twitter" },
  { href: "mailto:contact@example.com", icon: Mail, label: "Email" },
];

export function Footer() {
  return (
    <footer className="bg-surface-800 border-t border-surface-700">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="col-span-2 md:col-span-1">
            <Link
              href="/"
              className="font-display text-xl font-bold text-primary-glow"
            >
              The Omnitool
            </Link>
            <p className="mt-4 text-text-muted text-sm">
              A high-performance utility toolkit with 3D visualization.
            </p>
            {/* Social Links */}
            <div className="flex gap-4 mt-6">
              {socialLinks.map((social) => (
                <a
                  key={social.label}
                  href={social.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-text-muted hover:text-primary-glow transition-colors"
                  aria-label={social.label}
                >
                  <social.icon size={20} />
                </a>
              ))}
            </div>
          </div>

          {/* Links */}
          {footerLinks.map((section) => (
            <div key={section.title}>
              <h3 className="font-display font-semibold text-text-high mb-4">
                {section.title}
              </h3>
              <ul className="space-y-2">
                {section.links.map((link) => (
                  <li key={link.href}>
                    <Link
                      href={link.href}
                      className="text-text-muted hover:text-text-high transition-colors text-sm"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom Bar */}
        <div className="mt-12 pt-8 border-t border-surface-700">
          <p className="text-text-muted text-sm text-center">
            &copy; {new Date().getFullYear()} The Omnitool. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
