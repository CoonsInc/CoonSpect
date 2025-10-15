import Text from "../atoms/Text";

const Footer: React.FC = () => (
  <footer className="border-t border-purple-800/30 py-6 bg-[#0B0C1C] text-center">
    <Text size="sm" className="text-gray-500">
      © {new Date().getFullYear()} CoonSpect — все права защищены.
    </Text>
  </footer>
);

export default Footer;
