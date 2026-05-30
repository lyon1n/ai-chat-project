import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import Sidebar from "./Sidebar";

describe("Sidebar", () => {
  it("selects a knowledge base", async () => {
    const onSelectCollection = vi.fn();
    render(
      <Sidebar
        collections={[{ name: "demo", chunk_count: 3 }]}
        currentCollection=""
        onSelectCollection={onSelectCollection}
        onDeleteCollection={vi.fn()}
        onLogout={vi.fn()}
      />
    );

    await userEvent.click(screen.getByRole("button", { name: /demo/ }));

    expect(onSelectCollection).toHaveBeenCalledWith("demo");
  });
});
