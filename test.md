# Stress Test: Document Chunking and Semantic Retrieval

## 1. Abstract: The "Goldilocks" Paragraph
This is a standard-length paragraph. It is designed to be the "control" group for your chunker. It contains exactly four sentences. Most recursive character splitters should keep this entire block together. If your chunker splits this in the middle, your `chunk_size` is likely set too low.

---

## 2. Technical Data & LaTeX Integration
In RAG systems, formulas are often "hallucinated" if the context is split. This section tests if the explanation stays with the math.

The Gaussian distribution, often referred to as the "Normal Distribution," is defined by the following probability density function:

$$f(x) = \frac{1}{\sigma\sqrt{2\pi}} e^{-\frac{1}{2}\left(\frac{x-\mu}{\sigma}\right)^2}$$

> **Critical Context:** In the equation above, $\mu$ represents the mean or expectation of the distribution, while $\sigma$ represents the standard deviation. Splitting the document between the formula and this definition will result in a loss of vector meaning.

---

## 3. The Nested Hierarchy (Structural Integrity Test)
Lists are the most common victims of chunking. This section tests if your chunker preserves the relationship between a parent category and its sub-items.

* **Project Alpha**
    * **Phase 1: Discovery**
        * User Research and Persona Development
        * Competitive Landscape Analysis
    * **Phase 2: Execution**
        * Backend API Development (Node.js)
        * Frontend Component Library (React)
* **Project Beta**
    * Legacy System Migration
    * Documentation Overhaul

---

## 4. Tabular Data (The Table Break Test)
Tables are notoriously difficult for LLMs if the header is separated from the rows.

| Employee ID | Department       | Security Clearance | Last Audit Date |
| :---------- | :--------------- | :----------------- | :-------------- |
| 001-A       | Engineering      | Top Secret         | 2023-10-12      |
| 005-C       | Human Resources  | Confidential       | 2024-01-05      |
| 009-X       | Research & Dev   | Restricted         | 2023-11-20      |
| 012-B       | Executive Office | Top Secret         | 2024-02-14      |

---

## 5. Code Implementation (Syntactic Boundaries)
A code-aware chunker should recognize that the decorator, function signature, and docstring are a single semantic unit.

```python
@cache_results
def fetch_user_metadata(user_id: str) -> dict:
    """
    Retrieves metadata from the global cache. 
    If not found, it queries the primary SQL cluster.
    """
    import time
    # Simulate a network delay
    time.sleep(0.1)
    return {"id": user_id, "role": "admin", "status": "active"}

# This call depends on the function definition above
print(fetch_user_metadata("user_882"))