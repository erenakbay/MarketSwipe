import './Shopping.css';
import React, { useState } from 'react';
import { Link } from 'react-router-dom';  // Import Link from react-router-dom
import SwipeProducts from "../components/SwipeProducts";
import { useLocation } from 'react-router-dom';

const Shopping = () => {
  const { state } = useLocation();
  const { userId, email } = state || {};

  return (
    <div className="shopping-container">
      {/* Link to /cart with an image on the top right */}
      <Link to="/cart" className="cart-link">
        <img
          src="cart-icon.png" // Replace with your image path
          alt="Cart"
          className="cart-image"
        />
        <p  className="cart-text" >Shopping Cart</p> {/* Added text below the image */}
      </Link>

      <SwipeProducts />
    </div>
  );
};

export default Shopping;
