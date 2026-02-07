---
name: frontend-skill
description: Build responsive pages, reusable components, layouts, and apply styling for modern frontend applications.
---

# Frontend Skill

## Instructions

1. **Page & Layout Structure**
   - Create responsive pages that adapt to different screen sizes
   - Organize layouts with clear structure and hierarchy
   - Use grids, flexbox, or CSS frameworks effectively

2. **Components**
   - Build reusable and modular components
   - Maintain consistent design across the application
   - Implement state and props handling where needed

3. **Styling**
   - Apply styling using CSS, Tailwind, or CSS-in-JS
   - Ensure accessibility and readability
   - Support dark/light themes if required

## Best Practices
- Keep components small and focused
- Follow a consistent naming convention
- Optimize assets and styles for performance
- Ensure mobile-first design
- Reuse components to reduce code duplication

## Example Structure
```jsx
// Next.js page example
export default function HomePage() {
  return (
    <main className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
      <section className="text-center p-8">
        <h1 className="text-4xl font-bold animate-fade-in">Welcome to Our App</h1>
        <p className="mt-4 text-lg animate-fade-in-delay">
          Build responsive pages and reusable components
        </p>
        <button className="mt-6 px-6 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
          Get Started
        </button>
      </section>
    </main>
  );
}
```