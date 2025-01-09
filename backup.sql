-- MySQL dump 10.13  Distrib 9.1.0, for Win64 (x86_64)
--
-- Host: gateway01.ap-southeast-1.prod.aws.tidbcloud.com    Database: povertylens
-- ------------------------------------------------------
-- Server version	5.7.28-TiDB-Serverless

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `data_populasi`
--

DROP TABLE IF EXISTS `data_populasi`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `data_populasi` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `kelurahan` varchar(255) NOT NULL,
  `populasi` int(11) NOT NULL,
  `luas_wilayah` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`) /*T![clustered_index] CLUSTERED */
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin AUTO_INCREMENT=30001;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `data_populasi`
--

LOCK TABLES `data_populasi` WRITE;
/*!40000 ALTER TABLE `data_populasi` DISABLE KEYS */;
INSERT INTO `data_populasi` VALUES (1,'Kota tegal',290988,39.68),(2,'Tegal barat',69859,15.13),(3,'Pesurungan kidul',6337,0.72),(4,'Debong lor',4604,0.56),(5,'Kemandungan',3798,0.56),(6,'Pekauman',7812,0.96),(7,'Kraton',15897,1.23),(8,'Tegalsari',23359,2.19),(9,'Muarareja',8052,8.91),(10,'Tegal timur',86993,6.36),(11,'Kejambon',13777,0.86),(12,'Slerok',18793,1.39),(13,'Panggung',32312,2.23),(14,'Mangkukusuman',5445,0.47),(15,'Mintaragen',16666,1.41),(16,'Tegal selatan',71497,6.43),(17,'Kalinyamat wetan',5874,0.89),(18,'Bandung',6891,0.59),(19,'Debong kidul',6206,0.35),(20,'Tunon',7280,0.75),(21,'Keturen',5424,0.62),(22,'Debong kulon',5715,0.74),(23,'Debong tengah',14501,1.11),(24,'Randugunting',19606,1.38),(25,'Kel Margadana',62639,11.76),(26,'Kaligangsa',12128,2.53),(27,'Krandon',6847,1.2),(28,'Cabawan',6518,1.28),(29,'Kalinyamat kulon',6422,1.52),(30,'Margadana',16767,2.41),(31,'Sumurpanggang',7968,1),(32,'Pesurungan lor',5989,1.82);
/*!40000 ALTER TABLE `data_populasi` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `detail_lembaga`
--

DROP TABLE IF EXISTS `detail_lembaga`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `detail_lembaga` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `lembaga_id` int(11) NOT NULL,
  `alamat_kantor` varchar(255) DEFAULT NULL,
  `telepon` varchar(50) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `web_resmi` varchar(255) DEFAULT NULL,
  `deskripsi` text DEFAULT NULL,
  `informasi` text DEFAULT NULL,
  `nama_lengkap` text DEFAULT NULL,
  `kategori` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`) /*T![clustered_index] CLUSTERED */,
  KEY `fk_1` (`lembaga_id`),
  CONSTRAINT `fk_1` FOREIGN KEY (`lembaga_id`) REFERENCES `povertylens`.`lembaga` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin AUTO_INCREMENT=30002;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detail_lembaga`
--

LOCK TABLES `detail_lembaga` WRITE;
/*!40000 ALTER TABLE `detail_lembaga` DISABLE KEYS */;
INSERT INTO `detail_lembaga` VALUES (1,1,'Gedung Menara Taspen Lt. 1, Jl. Jend. Sudirman Kav. 2, Jakarta','021-50847142','baznas@baznas.go.id','https://baznas.go.id','Baznas bertanggung jawab menghimpun dan mengelola zakat, infak, dan sedekah, membantu distribusi dana untuk kemanusiaan, kesehatan, pendidikan, kebencanaan, dan pengembangan ekonomi.','Program termasuk bantuan kesehatan untuk masyarakat kurang mampu, beasiswa pendidikan, bantuan kebencanaan, serta pemberdayaan ekonomi bagi pelaku usaha kecil dan mikro.','Badan Amil Zakat Nasional','Kesehatan'),(2,2,'Jl. Sipelem No.2, Pekauman, Kec. Tegal Bar., Kota Tegal, Jawa Tengah 52112','(0283)355091','kontak@kemensos.go.id','https://dinsos.tegalkota.go.id/dtks/','Kemensos berfokus pada program kesejahteraan sosial dan perlindungan sosial di Indonesia','Program Keluarga Harapan (PKH) untuk keluarga miskin, bantuan sosial tunai, bantuan logistik untuk penyandang disabilitas, dan bantuan bencana.','Dinas Sosial Pemerintah Kota Tegal','Sosial dan Kesejahteraan'),(3,3,'Jl. Merdeka Selatan No. 5, Jakarta Pusat','021-34567890','info@lman.go.id','https://lman.go.id','LMAN mengelola aset negara dan menyediakan pembiayaan untuk proyek infrastruktur.','Pembiayaan infrastruktur dan pengelolaan aset negara yang optimal.\r\n','Lembaga Manajemen Aset Negara','Sosial dan Kesejahteraan'),(4,4,'Gedung SMF, Jl. Sisingamangaraja No. 2, Jakarta','021-57907000','pip.kemenkeu.go.id','https://pip.kemenkeu.go.id','PIP mendukung investasi jangka panjang dalam sektor riil.','Pembiayaan proyek di sektor riil, seperti infrastruktur dan usaha kecil menengah.','Pusat Investasi Pemerintah','Infrastruktur dan Ekonomi'),(5,5,'Jl. Pramuka Kav. 38, Jakarta','021-29827793','bnpb.go.id','https://bnpb.go.id','BNPB menangani koordinasi bantuan dan penanganan bencana.','Bantuan logistik, evakuasi, rehabilitasi, dan rekonstruksi bagi korban bencana.','Badan Nasional Penanggulangan Bencana','Bencana dan Penanggulangan'),(6,6,'Kantor dinas di masing-masing wilayah',NULL,NULL,NULL,'Menyediakan kesejahteraan sosial bagi masyarakat kurang mampu dan rentan.','Bantuan sosial tunai, rehabilitasi sosial, dan bantuan untuk masyarakat yang mengalami permasalahan sosial.','Dinas Sosial Daerah','Sosial dan Kesejahteraan'),(7,7,'Kantor-kantor Dinas Sosial di daerah',NULL,NULL,NULL,'Program untuk meningkatkan kondisi rumah masyarakat berpenghasilan rendah agar layak huni.','Renovasi rumah untuk meningkatkan kelayakan tempat tinggal.','Program Perbaikan Rumah Tidak Layak Huni',NULL),(8,8,'Sesuai lokasi wilayah masing-masing',NULL,NULL,NULL,'Memberikan layanan kesehatan dasar kepada masyarakat.','Layanan kesehatan preventif, pemeriksaan kesehatan, dan program vaksinasi.','Layanan Kesehatan Masyarakat','Kesehatan'),(9,9,'Jl. Ki.Gede Sebayu, Mangkukusuman, Kec. Tegal Timur, Kota Tegal, Jawa Tengah 52123','(0283)351008',NULL,'https://disdikbud.tegalkota.go.id/','Mengelola program pendidikan dan peningkatan kualitas pendidikan daerah.','Beasiswa, peningkatan fasilitas sekolah, bantuan operasional sekolah, dan pelatihan bagi tenaga pendidik.','Dinas Pendidikan dan Kebudayaan','Pendidikan'),(10,10,'Jl. Warung Jati Barat No. 14, Jakarta Selatan','021-27878888','dompetdhuafa.org','https://dompetdhuafa.org','Dompet Dhuafa adalah lembaga filantropi yang mendistribusikan zakat, infak, dan sedekah bagi masyarakat kurang mampu.','Program bantuan kesehatan, pendidikan, ekonomi, kebencanaan, dan pemberdayaan masyarakat?.','Dompet Dhuafa','Kesehatan'),(11,11,'Menara 165 Lt. 18, Jl. TB Simatupang, Jakarta Selatan','021-29406496','act.id','https://act.id','ACT adalah organisasi kemanusiaan yang fokus pada bantuan darurat di dalam dan luar negeri.','Bantuan kebencanaan, sosial, kesehatan, pendidikan, dan pengembangan ekonomi masyarakat di wilayah krisis.','Aksi Cepat Tanggap','Pengembangan Komunitas'),(12,12,'Jl. Raden Saleh Raya No. 48, Jakarta','021-3900456','wahanavisi.org','https://wahanavisi.org','Organisasi yang fokus pada pemberdayaan anak-anak dan pengembangan komunitas.','Program perlindungan anak, pendidikan, sanitasi, dan pengembangan ekonomi untuk meningkatkan kesejahteraan anak-anak.','Wahana Visi Indonesia','Pengembangan Komunitas'),(13,13,'Wisma Bakrie 2, Jl. H. R. Rasuna Said Kav B-2, Jakarta','021-3141308','undp.org','https://undp.org','Program PBB yang mendukung pembangunan berkelanjutan, pengentasan kemiskinan, dan pemberdayaan ekonomi.','Bantuan untuk pengentasan kemiskinan, perubahan iklim, dan pengembangan ekonomi berkelanjutan.','United Nations Development Programme','Infrastruktur dan Ekonomi'),(14,14,'Wisma Keiai, Jl. Jend. Sudirman Kav. 3, Jakarta','021-57851880','wfp.org','https://wfp.org','Organisasi PBB yang berfokus pada bantuan pangan dan gizi untuk wilayah yang menghadapi krisis pangan.','Bantuan pangan, nutrisi, dan ketahanan pangan, terutama di daerah krisis dan rawan pangan.','World Food Programme','Bencana dan Penanggulangan');
/*!40000 ALTER TABLE `detail_lembaga` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `kemiskinan`
--

DROP TABLE IF EXISTS `kemiskinan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `kemiskinan` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tahun` int(11) NOT NULL,
  `garis_kemiskinan` varchar(50) DEFAULT NULL,
  `jumlah_penduduk_miskin` varchar(50) DEFAULT NULL,
  `presentase_penduduk_miskin` varchar(50) DEFAULT NULL,
  `indeks_kedalaman_kemiskinan` varchar(50) DEFAULT NULL,
  `indeks_keparahan_kemiskinan` varchar(50) DEFAULT NULL,
  `gini_rasio` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`) /*T![clustered_index] CLUSTERED */
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin AUTO_INCREMENT=30003;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `kemiskinan`
--

LOCK TABLES `kemiskinan` WRITE;
/*!40000 ALTER TABLE `kemiskinan` DISABLE KEYS */;
INSERT INTO `kemiskinan` VALUES (1,2002,'115,809.00','31.700','13.300','1.790','0.340',''),(2,2003,'137,953.00','23.100','9.530','1.470','0.300',''),(3,2004,'167,621.00','23.100','9.490','1.240','0.240',''),(4,2005,'171,462.00','21.700','8.960','','','0.230'),(5,2006,'184,872.00','24.700','10.400','1.500','0.360','0.240'),(6,2007,'197,683.00','22.200','9.360','1.060','0.190','0.230'),(7,2008,'244,380.00','26.790','11.280','1.420','0.210','0.280'),(8,2009,'248,173.00','23.430','17.480','1.640','0.420','0.240'),(9,2010,'270,788.00','25.700','10.620','1.720','0.440','0.240'),(10,2011,'280,349.00','25.900','10.810','1.890','0.510','0.320'),(11,2012,'305,818.00','24.000','10.040','','','0.330'),(12,2013,'333,553.00','21.600','8.840','','','0.320'),(13,2014,'','','','','',''),(14,2015,'371,528.00','20.310','8.260','1.340','0.350',''),(15,2016,'295,631.00','20.260','8.200','1.040','0.210',''),(16,2017,'418,845.00','20.110','8.110','1.420','0.380',''),(17,2018,'455,488.00','19.440','7.810','1.230','0.300',''),(18,2019,'465,047.00','18.640','7.470','1.150','0.240',''),(19,2020,'502,031.00','19.550','7.800','1.380','0.360',''),(20,2021,'523,413.00','20.270','8.120','1.040','0.240','0.384'),(21,2022,'565,826.00','19.780','7.910','1.150','0.280','0.373'),(22,2023,'623,617.00','19.220','7.680','0.860','0.130','0.378');
/*!40000 ALTER TABLE `kemiskinan` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lembaga`
--

DROP TABLE IF EXISTS `lembaga`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lembaga` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nama` varchar(255) NOT NULL,
  `logo_url` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`) /*T![clustered_index] CLUSTERED */
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin AUTO_INCREMENT=30002;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lembaga`
--

LOCK TABLES `lembaga` WRITE;
/*!40000 ALTER TABLE `lembaga` DISABLE KEYS */;
INSERT INTO `lembaga` VALUES (1,'Baznas','/static/images/lembaga/baznas.png'),(2,'Kementerian Sosial Republik Indonesia','/static/images/lembaga/kemensos.png'),(3,'LMAN','/static/images/lembaga/lman.png'),(4,'PIP','/static/images/lembaga/pip.png'),(5,'BNPB','/static/images/lembaga/bnpb.png'),(6,'Dinas Sosial','/static/images/lembaga/baznas.png'),(7,'RTLH','/static/images/lembaga/baznas.png'),(8,'Puskesmas','/static/images/lembaga/puskesmas.png'),(9,'Dinas Pendidikan','/static/images/lembaga/pip.png'),(10,'Dompet Duafa','/static/images/lembaga/dompet-dhuafa.png'),(11,'ACT','/static/images/lembaga/act.png'),(12,'Wahana Visi Indonesia','/static/images/lembaga/wahana-visi.png'),(13,'UNDP','/static/images/lembaga/undp.png'),(14,'WFP','/static/images/lembaga/wfp.png');
/*!40000 ALTER TABLE `lembaga` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `luas_kelurahan`
--

DROP TABLE IF EXISTS `luas_kelurahan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `luas_kelurahan` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `kelurahan` varchar(100) NOT NULL,
  `luas_wilayah` float NOT NULL,
  PRIMARY KEY (`id`) /*T![clustered_index] CLUSTERED */
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin AUTO_INCREMENT=30001;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `luas_kelurahan`
--

LOCK TABLES `luas_kelurahan` WRITE;
/*!40000 ALTER TABLE `luas_kelurahan` DISABLE KEYS */;
INSERT INTO `luas_kelurahan` VALUES (1,'Tegal Selatan',6.43),(2,'Kalinyamat Wetan',0.89),(3,'Bandung',0.59),(4,'Debong Kidul',0.35),(5,'Tunon',0.75),(6,'Keturen',0.62),(7,'Debong Kulon',0.74),(8,'Debong Tengah',1.11),(9,'Randugunting',1.38),(10,'Tegal Timur',6.36),(11,'Kejambon',0.86),(12,'Slerok',1.39),(13,'Panggung',2.23),(14,'Mangkukusuman',0.47),(15,'Mintaragen',1.41),(16,'Tegal Barat',15.13),(17,'Pesurungan Kidul',0.72),(18,'Debong Lor',0.56),(19,'Kemandungan',0.56),(20,'Pekauman',0.96),(21,'Kraton',1.23),(22,'Tegalsari',2.19),(23,'Muarareja',8.91),(24,'Margadana',11.76),(25,'Kaligangsa',2.53),(26,'Krandon',1.2),(27,'Cabawan',1.28),(28,'Margadana',2.41),(29,'Kalinyamat Kulon',1.52),(30,'Sumurpanggang',1),(31,'Pesurungan Lor',1.82),(32,'Kota Tegal',39.68);
/*!40000 ALTER TABLE `luas_kelurahan` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ulasan_pengguna`
--

DROP TABLE IF EXISTS `ulasan_pengguna`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ulasan_pengguna` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ulasan` text NOT NULL,
  `label` varchar(255) NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `email` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`) /*T![clustered_index] CLUSTERED */
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin AUTO_INCREMENT=330001;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ulasan_pengguna`
--

LOCK TABLES `ulasan_pengguna` WRITE;
/*!40000 ALTER TABLE `ulasan_pengguna` DISABLE KEYS */;
INSERT INTO `ulasan_pengguna` VALUES (300001,'test','negatif','2025-01-06 17:21:04','oopzlyysky@gmail.com'),(300002,'asdasdasd','negatif','2025-01-06 17:21:41','oopzlyysky@gmail.com'),(300004,'aplikasinya bagus, mudah untuk digunakan','positif','2025-01-06 17:28:42','zaky@gmail.com');
/*!40000 ALTER TABLE `ulasan_pengguna` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(100) NOT NULL,
  `password_hash` varchar(256) NOT NULL,
  PRIMARY KEY (`id`) /*T![clustered_index] CLUSTERED */,
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin AUTO_INCREMENT=90001;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'admin','scrypt:32768:8:1$oFPGAtAM53HFAMBi$4b3ae51b32b56579b55b8599f3e87204e5d898762736d0f7f89345c719801a11c8d600eeaa01986af8fbe2f105df8d8b80566be0a869e9b419c35badbfe71c68'),(30001,'admin123','scrypt:32768:8:1$mrgu8v3m80WJ572X$5075958f4ffda529116d73368a7d6ba03c4181f9a43ca36ce04fc9b6e03ef95633d40e745237b3dfeedee5b224887bac8d6ae80a39db9d44363e140c04f5c4b4'),(60001,'veri','scrypt:32768:8:1$nt2PvjItrxJcwzPV$fe15007e32123310cc2b2d10c42d43c3325e0b4aac8c0f9b1215c3321ef98e823c6527264a815d13da02338106d95ac2a48953935c000293d19173621dbe131c');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-01-09  9:00:18
