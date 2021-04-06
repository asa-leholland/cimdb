--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.10
-- Dumped by pg_dump version 9.6.10

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: _employees; Type: TABLE; Schema: public; Owner: rebasedata
--

CREATE TABLE public._employees (
    employee_id integer,
    employee_group character varying(10) DEFAULT NULL::character varying,
    employee_first_name character varying(7) DEFAULT NULL::character varying,
    employee_last_name character varying(11) DEFAULT NULL::character varying,
    employee_email character varying(27) DEFAULT NULL::character varying,
    employee_password character varying(10) DEFAULT NULL::character varying,
    employee_site_id smallint
);


ALTER TABLE public._employees OWNER TO rebasedata;

--
-- Name: _locations; Type: TABLE; Schema: public; Owner: rebasedata
--

CREATE TABLE public._locations (
    location_id smallint,
    location_room_number smallint,
    location_shelf_number smallint,
    location_site_id smallint
);


ALTER TABLE public._locations OWNER TO rebasedata;

--
-- Name: _locationsregularcomps; Type: TABLE; Schema: public; Owner: rebasedata
--

CREATE TABLE public._locationsregularcomps (
    lrc_id smallint,
    lrc_location_id smallint,
    lrc_rc_pn smallint,
    lrc_quantity smallint
);


ALTER TABLE public._locationsregularcomps OWNER TO rebasedata;

--
-- Name: _products; Type: TABLE; Schema: public; Owner: rebasedata
--

CREATE TABLE public._products (
    product_sn smallint,
    product_pn character varying(8) DEFAULT NULL::character varying,
    product_family character varying(5) DEFAULT NULL::character varying,
    product_date_assembly character varying(10) DEFAULT NULL::character varying,
    product_qc_date character varying(10) DEFAULT NULL::character varying,
    product_warranty_expiration_date character varying(10) DEFAULT NULL::character varying,
    product_employee_id integer,
    product_location_id smallint,
    product_sc_sn smallint
);


ALTER TABLE public._products OWNER TO rebasedata;

--
-- Name: _productsregularcomps; Type: TABLE; Schema: public; Owner: rebasedata
--

CREATE TABLE public._productsregularcomps (
    prc_id smallint,
    prc_product_sn smallint,
    prc_rc_pn smallint,
    prc_quantity_needed smallint
);


ALTER TABLE public._productsregularcomps OWNER TO rebasedata;

--
-- Name: _regularcomponents; Type: TABLE; Schema: public; Owner: rebasedata
--

CREATE TABLE public._regularcomponents (
    rc_pn smallint,
    rc_pn_desc character varying(6) DEFAULT NULL::character varying,
    rc_category character varying(4) DEFAULT NULL::character varying
);


ALTER TABLE public._regularcomponents OWNER TO rebasedata;

--
-- Name: _sites; Type: TABLE; Schema: public; Owner: rebasedata
--

CREATE TABLE public._sites (
    site_id smallint,
    site_address_1 character varying(21) DEFAULT NULL::character varying,
    site_address_2 character varying(9) DEFAULT NULL::character varying,
    site_address_city character varying(13) DEFAULT NULL::character varying,
    site_address_state character varying(2) DEFAULT NULL::character varying,
    site_address_postal_code integer
);


ALTER TABLE public._sites OWNER TO rebasedata;

--
-- Name: _specialcomponents; Type: TABLE; Schema: public; Owner: rebasedata
--

CREATE TABLE public._specialcomponents (
    sc_sn smallint,
    sc_pn character varying(2) DEFAULT NULL::character varying,
    sc_is_free smallint,
    sc_product_sn character varying(1) DEFAULT NULL::character varying,
    sc_location_id smallint
);


ALTER TABLE public._specialcomponents OWNER TO rebasedata;

--
-- Name: _workorderproducts; Type: TABLE; Schema: public; Owner: rebasedata
--

CREATE TABLE public._workorderproducts (
    wop_id smallint,
    wop_wo_id integer,
    wop_product_sn smallint
);


ALTER TABLE public._workorderproducts OWNER TO rebasedata;

--
-- Name: _workorders; Type: TABLE; Schema: public; Owner: rebasedata
--

CREATE TABLE public._workorders (
    wo_id integer,
    wo_open_date character varying(10) DEFAULT NULL::character varying,
    wo_close_date character varying(10) DEFAULT NULL::character varying,
    wo_status character varying(16) DEFAULT NULL::character varying,
    wo_reference_number integer,
    wo_employee_id integer
);


ALTER TABLE public._workorders OWNER TO rebasedata;

--
-- Data for Name: _employees; Type: TABLE DATA; Schema: public; Owner: rebasedata
--

COPY public._employees (employee_id, employee_group, employee_first_name, employee_last_name, employee_email, employee_password, employee_site_id) FROM stdin;
14324	supervisor	Pam	Luddy	pluddy6@2fast4you.com	CcBwnjq	16
35477	production	Giulia	Comberbeach	gcomberbeach7@2fast4you.com	oxAFg4t	16
39816	production	Kalindi	Shulem	kshulem0@2fast4you.com	DJi02w0oV2	16
61764	production	Kaiser	Reina	kreina4@2fast4you.com	KnrAKdA	16
\.


--
-- Data for Name: _locations; Type: TABLE DATA; Schema: public; Owner: rebasedata
--

COPY public._locations (location_id, location_room_number, location_shelf_number, location_site_id) FROM stdin;
1	0	0	1
52	1	1	16
53	1	2	16
54	1	3	16
55	1	4	16
56	1	5	16
57	2	1	16
58	2	2	16
59	2	3	16
60	2	4	16
61	2	5	16
62	3	1	16
63	3	2	16
64	3	3	16
65	3	4	16
66	3	5	16
67	4	1	16
68	4	2	16
69	4	3	16
70	4	4	16
71	4	5	16
72	5	1	16
73	5	2	16
74	5	3	16
75	5	4	16
76	5	5	16
\.


--
-- Data for Name: _locationsregularcomps; Type: TABLE DATA; Schema: public; Owner: rebasedata
--

COPY public._locationsregularcomps (lrc_id, lrc_location_id, lrc_rc_pn, lrc_quantity) FROM stdin;
1	4	1	0
2	64	2	1
3	69	3	3
4	43	50	14
5	14	51	25
6	35	52	0
7	45	150	234
8	15	151	62
9	30	152	73
10	68	1	25
11	34	2	74
12	31	3	95
13	13	50	4
14	24	51	0
15	72	52	0
16	57	150	234
17	29	151	7
18	58	152	33
19	67	1	0
20	5	2	237
21	61	3	88
22	65	50	81
23	59	51	26
24	54	52	0
25	11	150	42
26	25	151	27
27	71	152	25
28	38	1	238
29	7	2	42
30	53	3	265
31	40	50	23
32	26	51	8
33	63	52	0
34	48	150	0
35	16	151	2
36	22	152	4
\.


--
-- Data for Name: _products; Type: TABLE DATA; Schema: public; Owner: rebasedata
--

COPY public._products (product_sn, product_pn, product_family, product_date_assembly, product_qc_date, product_warranty_expiration_date, product_employee_id, product_location_id, product_sc_sn) FROM stdin;
1	Pro-i3	Pro	2020-12-20	2020-12-12	2021-12-21	61764	57	3001
2	Pro-i3	Pro	2020-12-20	2020-12-12	2021-12-21	39816	57	3002
3	Basic-i3	Basic	2020-12-20	2020-12-12	2021-12-21	35477	57	3003
4	Pro-i5	Pro	2020-12-20	2020-12-12	2021-12-21	61764	57	5001
5	Pro-i5	Pro	2020-12-20	2020-12-12	2021-12-21	39816	57	5002
6	Basic-i5	Basic	2020-12-20	2020-12-12	2021-12-21	35477	57	5003
7	Pro-i7	Pro	2020-12-20	2020-12-12	2021-12-21	61764	57	7001
8	Basic-i7	Basic	2020-12-20	2020-12-12	2021-12-21	39816	57	7002
9	Basic-i7	Basic	2020-12-20	2020-12-12	2021-12-21	35477	57	7003
10	Pro-i7	Pro	2020-12-20	2020-12-12	2021-12-21	61764	57	7004
\.


--
-- Data for Name: _productsregularcomps; Type: TABLE DATA; Schema: public; Owner: rebasedata
--

COPY public._productsregularcomps (prc_id, prc_product_sn, prc_rc_pn, prc_quantity_needed) FROM stdin;
1	1	1	1
2	1	50	2
3	1	100	1
4	1	150	2
5	1	200	1
6	2	3	1
7	2	51	3
8	2	102	1
9	2	152	1
10	2	200	1
11	3	3	1
12	3	52	3
13	3	100	1
14	3	151	3
15	3	202	1
16	4	3	1
17	4	50	2
18	4	100	1
19	4	150	2
20	4	200	1
\.


--
-- Data for Name: _regularcomponents; Type: TABLE DATA; Schema: public; Owner: rebasedata
--

COPY public._regularcomponents (rc_pn, rc_pn_desc, rc_category) FROM stdin;
1	MB 1	MB
2	MB 2	MB
3	MB 3	MB
50	RAM 1	RAM
51	RAM 2	RAM
52	RAM 3	RAM
100	Case 1	Case
101	Case 2	Case
102	Case 3	Case
150	HDD 1	HDD
151	HDD 2	HDD
152	HDD 3	HDD
200	NO GC	GC
201	GC 1	GC
202	GC 2	GC
\.


--
-- Data for Name: _sites; Type: TABLE DATA; Schema: public; Owner: rebasedata
--

COPY public._sites (site_id, site_address_1, site_address_2, site_address_city, site_address_state, site_address_postal_code) FROM stdin;
1	Customer	Customer	Customer	CA	99999
12	12745 Lampwood Road	Suite 612	Los Angeles	CA	90023
14	26262 Shoreline Drive		San Francisco	CA	94125
16	1984 Washoe Street		Reno	NV	89523
\.


--
-- Data for Name: _specialcomponents; Type: TABLE DATA; Schema: public; Owner: rebasedata
--

COPY public._specialcomponents (sc_sn, sc_pn, sc_is_free, sc_product_sn, sc_location_id) FROM stdin;
3000	i3	0		57
3001	i3	0		57
3002	i3	0		57
3003	i3	1		57
3004	i3	1		57
3005	i3	1		57
3006	i3	1		57
3007	i3	1		57
3008	i3	1		57
3009	i3	1		57
5000	i5	1		57
5001	i5	0		57
5002	i5	0		57
5003	i5	0		57
5004	i5	1		57
5005	i5	1		57
5006	i5	1		57
5007	i5	1		57
5008	i5	1		57
5009	i5	1		57
7000	i7	0		57
7001	i7	0		57
7002	i7	0		57
7003	i7	1		57
7004	i7	1		57
7005	i7	1		57
7006	i7	1		57
7007	i7	1		57
7008	i7	1		57
7009	i7	1		57
\.


--
-- Data for Name: _workorderproducts; Type: TABLE DATA; Schema: public; Owner: rebasedata
--

COPY public._workorderproducts (wop_id, wop_wo_id, wop_product_sn) FROM stdin;
1	879845	1
2	815348	2
3	845236	3
4	879845	4
5	815348	5
6	845236	6
7	879845	7
8	815348	8
9	845236	9
10	879845	10
\.


--
-- Data for Name: _workorders; Type: TABLE DATA; Schema: public; Owner: rebasedata
--

COPY public._workorders (wo_id, wo_open_date, wo_close_date, wo_status, wo_reference_number, wo_employee_id) FROM stdin;
815348	2021-01-12		qc_pending	84325	39816
845236	2021-01-24	2021-01-16	shipping_pending	23165	35477
879845	2021-01-29		assembly_pending	84596	61764
\.


--
-- PostgreSQL database dump complete
--

