import { useState, useEffect } from "react";
import axios from "axios";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import {
  Select,
  Button,
  Typography,
  Card,
  Row,
  Col,
  Divider,
  Upload,
  Empty,
} from "antd";
import { UploadOutlined } from "@ant-design/icons";

const { Title, Text } = Typography;
const { Option } = Select;

function FurniturePlacementTest() {
  const [roomDesigns, setRoomDesigns] = useState([]);
  const [selectedDesignId, setSelectedDesignId] = useState(null);
  const [furnitureFiles, setFurnitureFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  useEffect(() => {
    fetchRoomDesigns();
  }, []);

  const fetchRoomDesigns = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:8000/api/room-designs/list");
      setRoomDesigns(response.data.designs || []);
    } catch (error) {
      toast.error("Failed to fetch room designs");
      console.error(error);
    }
  };

  const handleFurnitureUpload = (info) => {
    const fileList = info.fileList.map(file => file.originFileObj || file);
    setFurnitureFiles(fileList);
  };

  const handleSubmit = async () => {
    if (!selectedDesignId) {
      toast.error("Please select a room design");
      return;
    }

    if (furnitureFiles.length === 0) {
      toast.error("Please upload at least one furniture image");
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append("room_design_id", selectedDesignId);

    furnitureFiles.forEach((file) => {
      formData.append("furniture_images", file);
    });

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/api/furniture-placement",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      setResult({
        image: response.data.image,
        text: response.data.text,
      });

      toast.success("Furniture placed successfully!");
    } catch (error) {
      toast.error("Furniture placement failed");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const selectedDesign = roomDesigns.find((d) => d.id === selectedDesignId);

  return (
    <div style={{ padding: "2rem", maxWidth: "1400px", margin: "0 auto" }}>
      <Title level={2} style={{ textAlign: "center", marginBottom: "2rem" }}>
        Furniture Placement Test Page
      </Title>

      <Row gutter={[24, 24]}>
        <Col xs={24} lg={12}>
          <Card title="Step 1: Select Room Design" style={{ marginBottom: 24 }}>
            <Select
              placeholder="Select a generated room design"
              style={{ width: "100%", marginBottom: 16 }}
              value={selectedDesignId}
              onChange={setSelectedDesignId}
            >
              {roomDesigns.map((design) => (
                <Option key={design.id} value={design.id}>
                  {design.room_type} - {design.style} ({new Date(design.created_at).toLocaleDateString()})
                </Option>
              ))}
            </Select>

            {selectedDesign && (
              <div>
                <img
                  src={selectedDesign.generated_image_url}
                  alt="Selected room design"
                  style={{
                    width: "100%",
                    borderRadius: 8,
                    boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
                  }}
                />
                <div style={{ marginTop: 12 }}>
                  <Text strong>Room Type:</Text> {selectedDesign.room_type}<br />
                  <Text strong>Style:</Text> {selectedDesign.style}<br />
                  <Text strong>Design Type:</Text> {selectedDesign.design_type}
                </div>
              </div>
            )}
          </Card>

          <Card title="Step 2: Upload Furniture Images">
            <Upload
              multiple
              listType="picture"
              beforeUpload={() => false}
              onChange={handleFurnitureUpload}
              accept="image/*"
            >
              <Button icon={<UploadOutlined />}>Upload Furniture Images</Button>
            </Upload>

            <div style={{ marginTop: 24, textAlign: "center" }}>
              <Button
                type="primary"
                size="large"
                onClick={handleSubmit}
                loading={loading}
                disabled={!selectedDesignId || furnitureFiles.length === 0}
              >
                {loading ? "Placing Furniture..." : "Place Furniture in Room"}
              </Button>
            </div>
          </Card>
        </Col>

        <Col xs={24} lg={12}>
          <Card title="Result">
            {result ? (
              <div>
                <img
                  src={result.image}
                  alt="Room with furniture"
                  style={{
                    width: "100%",
                    borderRadius: 8,
                    boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
                    marginBottom: 16,
                  }}
                />
                <div
                  style={{
                    background: "#f5f5f5",
                    padding: "1rem",
                    borderRadius: 8,
                    maxHeight: "300px",
                    overflowY: "auto",
                  }}
                >
                  <Text strong>Placement Description:</Text>
                  <div style={{ marginTop: 8, whiteSpace: "pre-wrap" }}>
                    {result.text}
                  </div>
                </div>
              </div>
            ) : (
              <Empty description="No result yet. Upload furniture and click 'Place Furniture in Room'" />
            )}
          </Card>
        </Col>
      </Row>

      <ToastContainer />
    </div>
  );
}

export default FurniturePlacementTest;
