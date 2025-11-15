import { Outlet, Link, useLocation } from "react-router-dom";
import { Layout as AntLayout, Menu } from "antd";
import { HomeOutlined, AppstoreAddOutlined } from "@ant-design/icons";

const { Header, Content } = AntLayout;

function Layout() {
  const location = useLocation();

  const menuItems = [
    {
      key: "/",
      icon: <HomeOutlined />,
      label: <Link to="/">Room Designer</Link>,
    },
    {
      key: "/furniture-placement",
      icon: <AppstoreAddOutlined />,
      label: <Link to="/furniture-placement">Furniture Placement Test</Link>,
    },
  ];

  return (
    <AntLayout style={{ minHeight: "100vh" }}>
      <Header style={{ display: "flex", alignItems: "center", padding: "0 20px" }}>
        <div style={{ color: "white", fontSize: "20px", fontWeight: "bold", marginRight: "40px" }}>
          AI Home Designer
        </div>
        <Menu
          theme="dark"
          mode="horizontal"
          selectedKeys={[location.pathname]}
          items={menuItems}
          style={{ flex: 1, minWidth: 0 }}
        />
      </Header>
      <Content>
        <Outlet />
      </Content>
    </AntLayout>
  );
}

export default Layout;
