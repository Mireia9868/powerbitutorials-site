// ============================================================
// 02 — MARKET BASKET — build the pair table from a line-item fact.
// Source query `SalesLines` must have: OrderKey, Product.
// Paste into Power Query (Advanced Editor) as a new query.
// ============================================================

let
    Source = SalesLines,

    // Keep distinct products per order so a repeated line does not
    // create a phantom pair.
    DistinctPairs = Table.Distinct(
        Table.SelectColumns(Source, {"OrderKey", "Product"})
    ),

    // Self-join on OrderKey, then keep only A < B to avoid duplicates
    // and self-pairs.
    Join = Table.NestedJoin(
        DistinctPairs, {"OrderKey"},
        DistinctPairs, {"OrderKey"},
        "Other", JoinKind.Inner
    ),
    Expand = Table.ExpandTableColumn(
        Join, "Other", {"Product"}, {"ProductB"}
    ),
    Renamed = Table.RenameColumns(
        Expand, {{"Product", "ProductA"}}
    ),
    Ordered = Table.SelectRows(
        Renamed, each [ProductA] < [ProductB]
    ),
    BasketPairs = Table.SelectColumns(
        Ordered, {"OrderKey", "ProductA", "ProductB"}
    ),

    // Single-product table for the Support(A) / Support(B) denominators.
    BasketSingles = Table.Distinct(
        Table.SelectColumns(Source, {"OrderKey", "Product"})
    )
in
    [BasketPairs = BasketPairs, BasketSingles = BasketSingles]
