const Footer = () => {
    return (
      <footer className="bg-black text-white py-8 px-4">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Column 1 */}
            <div className="space-y-4">
              <h3 className="text-xl font-bold">About Us</h3>
              <p className="text-gray-400">
                Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore.
              </p>
            </div>
  
            {/* Column 2 */}
            <div className="space-y-4">
              <h3 className="text-xl font-bold">Quick Links</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">Home</a></li>
                <li><a href="#" className="hover:text-white transition-colors">About</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Services</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Contact</a></li>
              </ul>
            </div>
  
            {/* Column 3 */}
            <div className="space-y-4">
              <h3 className="text-xl font-bold">Contact</h3>
              <ul className="space-y-2 text-gray-400">
                <li>Email: info@example.com</li>
                <li>Phone: (123) 456-7890</li>
                <li>Address: 123 Street Name, City</li>
              </ul>
            </div>
          </div>
  
          {/* Copyright */}
          <div className="border-t border-gray-800 mt-8 pt-6 text-center text-gray-400">
            <p>
              &copy; {new Date().getFullYear()} Your Company Name. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    );
  };
  
  export default Footer;