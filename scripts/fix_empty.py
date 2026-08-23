with open(r"C:\IEMS\static\css\components.css", "a", encoding="utf-8") as f:
    f.write("\n" + """
/* --------------------------------------------------------------------------
   8. EMPTY STATES (Premium)
   -------------------------------------------------------------------------- */
.k-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  background: white;
  border-radius: 12px;
  border: 1px dashed var(--color-border-strong, #CBD5E1);
  text-align: center;
  margin: 24px 0;
}
.k-empty-state svg {
  color: var(--color-text-muted, #94A3B8);
  margin-bottom: 16px;
  width: 48px;
  height: 48px;
  opacity: 0.8;
}
.k-empty-state h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-title, #0F172A);
  margin: 0 0 8px 0;
}
.k-empty-state p {
  font-size: 14px;
  color: var(--color-text-secondary, #64748B);
  margin: 0 0 24px 0;
  max-width: 400px;
}
""")
print("Added Empty State CSS")
