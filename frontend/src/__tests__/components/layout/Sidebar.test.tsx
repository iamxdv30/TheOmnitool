import "@testing-library/jest-dom";
import { render, screen } from "@testing-library/react";
import { Sidebar } from "@/components/layout";
import { useUIStore } from "@/store/uiStore";

jest.mock("@/components/layout/ThemeToggle", () => ({
  ThemeToggle: () => <button type="button">Toggle theme</button>,
}));

jest.mock("@/hooks", () => ({
  useAuth: () => ({ logout: jest.fn() }),
}));

describe("Sidebar", () => {
  beforeEach(() => {
    useUIStore.setState({ isSidebarCollapsed: false });
  });

  it("uses All tools as the single tool-library destination", () => {
    render(<Sidebar />);

    expect(screen.getByRole("link", { name: "All tools" })).toHaveAttribute(
      "href",
      "/tools"
    );
    expect(screen.queryByText("Tax Calculator")).not.toBeInTheDocument();
    expect(screen.queryByText("Character Counter")).not.toBeInTheDocument();
    expect(screen.queryByText("Unix Timestamp")).not.toBeInTheDocument();
    expect(screen.queryByText("Email Templates")).not.toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "Settings" })).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Back" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Log out" })).toBeInTheDocument();
  });

  it("keeps the brand mark visible when the sidebar is collapsed", () => {
    useUIStore.setState({ isSidebarCollapsed: true });

    render(<Sidebar />);

    expect(screen.getByTitle("Omnitool Dashboard")).toBeInTheDocument();
  });
});
