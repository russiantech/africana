To implement the client's new requirements into your existing inventory and sales reporting system, you can extend the design with some key adjustments, ensuring that stock is apportioned and tracked at different levels. Here's a seamless approach:

### Key Concepts:
1. Main Product (A): The original large bag (e.g., a bag of rice).
2. Apportioned Stock (B): Smaller bags created from the main product (e.g., a smaller bag containing rice).
3. Extracted Stock (C): Even smaller portions extracted from the apportioned stock, to be sold as different varieties (e.g., rice used to make jollof rice or fried rice).
4. Sales Varieties (Jollof Rice, Fried Rice, etc.): Products sold at different prices, derived from the extracted stock.

### Step-by-Step Design:

1. Add Hierarchical Stock Management:
   - Model Update: Update your inventory models to track different levels of stock.
     - Stock A (Large Bags): Main bag of rice, tracked with its original quantity.
     - Stock B (Smaller Bags): Smaller portions of the large bag, tracked by the number of small bags derived from the large bag.
     - Stock C (Small Portions): Tiny portions used for each sale variety, tracked by quantity used to prepare dishes.

   Here's a potential data structure:
   ```python
   class StockA(db.Model):  # Large Bag
       id = db.Column(db.Integer, primary_key=True)
       name = db.Column(db.String(100), nullable=False)  # e.g., Bag of Rice A
       quantity = db.Column(db.Float, nullable=False)    # e.g., Total weight of rice

   class StockB(db.Model):  # Apportioned Smaller Bag
       id = db.Column(db.Integer, primary_key=True)
       stock_a_id = db.Column(db.Integer, db.ForeignKey('stock_a.id'), nullable=False)
       quantity = db.Column(db.Float, nullable=False)    # e.g., 37 smaller bags

   class StockC(db.Model):  # Small Portions from Smaller Bags
       id = db.Column(db.Integer, primary_key=True)
       stock_b_id = db.Column(db.Integer, db.ForeignKey('stock_b.id'), nullable=False)
       quantity = db.Column(db.Float, nullable=False)    # e.g., specific portions for sales
   ```

2. Apportioning Logic (A to B):
   - When Stock A (e.g., bag of rice) is apportioned, create Stock B entries (e.g., smaller bags of rice).
   - Reduce the quantity of Stock A accordingly.
   
   ```python
   def apportion_stock_a_to_b(stock_a, num_small_bags):
       total_weight = stock_a.quantity
       weight_per_bag = total_weight / num_small_bags
       for i in range(num_small_bags):
           stock_b = StockB(stock_a_id=stock_a.id, quantity=weight_per_bag)
           db.session.add(stock_b)
       stock_a.quantity -= total_weight
       db.session.commit()
   ```

3. Extraction Logic (B to C):
   - When stock is extracted from Stock B to Stock C for preparing dishes, reduce Stock B based on the portion sizes.
   
   ```python
   def extract_from_b_to_c(stock_b, num_small_portions):
       portion_size = stock_b.quantity / num_small_portions
       for i in range(num_small_portions):
           stock_c = StockC(stock_b_id=stock_b.id, quantity=portion_size)
           db.session.add(stock_c)
       stock_b.quantity -= (portion_size * num_small_portions)
       db.session.commit()
   ```

4. Sales Logic (C to Final Product):
   - When a sale is made (e.g., jollof rice, fried rice), reduce the quantity from Stock C, depending on the portion size required for each type of dish. Track the sales with different varieties and prices.
   
   ```python
   class Sale(db.Model):
       id = db.Column(db.Integer, primary_key=True)
       variety = db.Column(db.String(100), nullable=False)  # e.g., jollof rice, fried rice
       price = db.Column(db.Float, nullable=False)
       quantity_sold = db.Column(db.Float, nullable=False)  # Portion sold (from C)
       stock_c_id = db.Column(db.Integer, db.ForeignKey('stock_c.id'), nullable=False)

   def sell_rice(variety, quantity_sold, price, stock_c):
       sale = Sale(variety=variety, quantity_sold=quantity_sold, price=price, stock_c_id=stock_c.id)
       stock_c.quantity -= quantity_sold
       db.session.add(sale)
       db.session.commit()
   ```

5. Reporting:
   - Ensure that your sales reporting can differentiate between the types of rice sold (e.g., jollof, fried rice) and their corresponding prices.
   - Track inventory reductions at each stage:
     - Stock A reduces based on the number of small bags apportioned.
     - Stock B reduces based on how many portions are extracted for sales.
     - Stock C reduces when specific varieties are sold.

### Example Workflow:
1. Apportion Stock A (a large bag of rice) into 37 smaller bags (Stock B).
2. Extract portions (Stock C) from the smaller bags for preparing dishes.
3. Sell dishes like jollof rice or fried rice, reducing the corresponding Stock C and recording sales.

### Integration with Existing Design:
- Ensure that the new models for Stock B and Stock C are integrated with your existing stock model.
- Update your current inventory management and sales tracking processes to include the new logic for apportioning and extracting stock at different levels.
- Modify your existing sales reports to account for the different varieties of dishes and their corresponding prices.

By carefully integrating these changes into your current system, you can maintain a seamless workflow while enhancing your inventory and sales tracking capabilities.


===========================================================================================================
apportion, varieties, profit n loss
===========================================================================================================

Note !mportant: as a tip, allow them be able to create new product/product-combinations and insert sales per day/sales to be generated. 
Like, rice and salad with price sold at by them.

I have inventory management system, and it's workiing perfect. But recently client gave the folloowing requirements, that must be implimented with existing design and sales reporting pattern. How can these be done seamlessly with existing design..?


> A bag of rice A can be apportioned into 37 small bags B;
> From this 37 bag(B), stock can be extracted from it like 3 small bag C. Quantity should be reduced for (B) at this point based on number of C.
> From this stock (C), sales can be generated for different varieties with different prices like jollof rice - N3500, fried rice - 2300, etc,
 Quantity should also be reduced for (C) at this point also. Then sales will be tract based on different varieties and corresponding prices.

Chips:

> Yam
> Yam & egg sauce

> Also give flexibility for custom products like chips & chicken
> chips has no stock
> chicken has stock but chips does not have stock
> we have chicken & chips 

Complimentaries like:
chips, etc. for dishes like chicken n chips(complimentary)
bread (complimentary for cow tail & goat meat pepper soup)

Ensure cost price is calculated.

omega tequilla(32 pcs of glass), but not sold in tots(glass)
omega sierra (30 pcs of small glass inside)

For the fact that some people buy chicken and salad, and different varieties, so they(workers) should be able to record such as need be.

Update to include cost price instock also. Such that cost price minus selling price will give us profit.