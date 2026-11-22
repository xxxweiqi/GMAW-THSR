# MBGN｜GMAW 过程内缺陷检测中英对照读稿

Zhao 等，*Mechanical Systems and Signal Processing* 258 (2026), 114696。正式发表版 20 页。 [DOI](https://doi.org/10.1016/j.ymssp.2026.114696)

**章节**　[引言](#S006) · [实验与模型](#S017) · [结果与讨论](#S061) · [结论](#S106) · [局限](#S110) · [参考文献](#S122) · [精读与选题启发](#reading-notes)

**PDF 页码**　[1](#S001) · [2](#S007) · [3](#S016) · [4](#S028) · [5](#F003) · [6](#T002) · [7](#S032) · [8](#S042) · [9](#S053) · [10](#T005) · [11](#S064) · [12](#S075) · [13](#S075) · [14](#S082) · [15](#S085) · [16](#S088) · [17](#S091) · [18](#S095) · [19](#S109) · [20](#S119)

图表放在首次展开讨论的段落附近，图表标题下标注原页码。段落跨页时保留起止页。原文口径与术语核对见[翻译说明](translation_notes.md)。

## 文献信息

<a id="S001"></a>
**Source**　p.1 · S001

**Original:**

MBGN: multimodal BiFPN gate network for in-process GMAW  
defect detection  
Xuefeng Zhao a , Yang She a , Giulio Mattera d , Lichao Hu e, Zhen Sun f, Yan Li c ,  
Xinghua Yu a,b,*  
a  
  School of Materials Science & Engineering, Beijing Institute of Technology, 100081 Beijing, the People's Republic of China  
b  
  Materials Intelligent Innovation Laboratory (MIIL), Beijing Institute of Technology, Zhuhai, Guangdong 519088, the People's Republic of China  
c  
  Chongqing Innovation Center, Beijing Institute of Technology, 401147 Chongqing, the People's Republic of China  
d  
  Department of Chemical, Materials and Industrial Production Engineering, University of Naples Federico II, Italy  
e  
  Chongqing Midea General Refrigeration Equipment Co., Ltd, 401336 Chongqing, the People's Republic of China  
f  
  Engineering Training Center, Shandong University, 250002 Jinan, the People's Republic of China

**译文:** **题名**　MBGN：用于 GMAW 过程内缺陷检测的多模态 BiFPN 门控网络

**作者**　Xuefeng Zhao、Yang She、Giulio Mattera、Lichao Hu、Zhen Sun、Yan Li、Xinghua Yu（通讯作者）。

**单位**　(a) 北京理工大学材料科学与工程学院，北京 100081。(b) 北京理工大学材料智能创新实验室（MIIL），广东珠海 519088。(c) 北京理工大学重庆创新中心，重庆 401147。(d) 那不勒斯费德里科二世大学化学、材料与工业生产工程系，意大利那不勒斯。(e) 重庆美的通用制冷设备有限公司，重庆 401336。(f) 山东大学工程训练中心，济南 250002。

<a id="S002"></a>
**Source**　p.1 · S002

**Original:** * Corresponding author at: School of Materials Science & Engineering, Beijing Institute of Technology, 100081 Beijing, the People's Republic of China. E-mail address: xyu@bit.edu.cn (X. Yu).

**译文:** 通讯作者单位为北京理工大学材料科学与工程学院，北京 100081。电子邮箱为 xyu@bit.edu.cn。

<a id="S003"></a>
**Source**　p.1 · S003

**Original:** https://doi.org/10.1016/j.ymssp.2026.114696 Received 12 March 2026; Received in revised form 8 June 2026; Accepted 11 July 2026 Available online 14 July 2026 0888-3270/© 2026 Elsevier Ltd. All rights are reserved, including those for text and data mining, AI training, and similar technologies.

**译文:** DOI 为 10.1016/j.ymssp.2026.114696。2026 年 3 月 12 日收稿，6 月 8 日收到修订稿，7 月 11 日接收，7 月 14 日在线可读。ISSN 0888-3270，© 2026 Elsevier Ltd. 保留所有权利，包括用于文本与数据挖掘、人工智能训练及类似技术的权利。

<a id="S004"></a>
**Source**　p.1 · S004

**Original:** Communicated by Eleni Chatzi  
  
Keywords: Weld, Deep learning, Multimodal, In-process monitoring, Defect detection

**译文:** 编辑经办：Eleni Chatzi。关键词：焊接、深度学习、多模态、过程内监测、缺陷检测。

## 摘要

<a id="S005"></a>
**Source**　p.1 · S005

**Original:** In-process defect monitoring is critical for guaranteeing the integrity of Gas Metal Arc Welding (GMAW) joints. Conventional non-destructive testing (NDT) delivers high-quality diagnostics only after the weld has finished, precluding immediate corrective action. We present the Multi-modal BiFPN Gate Network (MBGN), a deep-learning framework that fuses two complementary data streams: (i) time-synchronized welding current and voltage waveforms processed by a one-dimensional CNN, and (ii) high-speed molten-pool imagery processed by a ResNet backbone. The two modalities are merged through a Bidirectional Feature Pyramid Network (BiFPN), and a lightweight Gate module adaptively recalibrates cross-modal interactions before a final classifier. Experiments on an industrially collected multimodal dataset demonstrate that MBGN achieved 0.748 accuracy and 0.719 macro-F1 on the held-out evaluation set. Compared with the strongest task-matched multimodal baseline, MWFN, MBGN improved macro-F1 by 0.120 while maintaining comparable accuracy. These results indicate the potential of multimodal fusion for in-process GMAW defect monitoring under the investigated industrial conditions, while broader deployment still requires validation across additional materials, joint types, and online system configurations.

**译文:** 过程内缺陷监测对保证熔化极气体保护焊（GMAW）接头的完整性至关重要。传统无损检测（NDT）能提供高质量的诊断，但只能在焊接完成后开展，因此无法立即纠偏。本文提出多模态 BiFPN 门控网络（MBGN），用两个互补的数据流进行深度融合。（1）时间同步的焊接电流、电压波形，由一维 CNN 处理。（2）熔池高速图像，由 ResNet 主干网络处理。双向特征金字塔网络（BiFPN）融合两种模态，轻量门控模块在分类前自适应地重校准跨模态交互。工业采集数据实验表明，MBGN 在留出的评估集上达到 0.748 准确率和 0.719 宏平均 F1。与任务匹配的最强多模态基线 MWFN 相比，宏平均 F1 提升 0.120，且准确率相近。这些结果表明，多模态融合在本文考察的工业条件下具有过程内监测潜力。更广泛的部署仍需在更多材料、接头形式及在线系统配置下验证。

<a id="S006"></a>
## 1. 引言

**Source**　p.1 · S006

**Original:** 1. Introduction

**译文:** 1. 引言

<a id="S007"></a>
**Source**　pp.1–2 · S007

**Original:** Gas Metal Arc Welding (GMAW) is a cornerstone of contemporary fabrication, prized for its high throughput, compatibility with automation, and capacity to produce welds of consistently high quality[1]. Industries that demand structural integrity-automotive, shipbuilding, energy, and aerospace-rely on GMAW to fabricate critical components whose safety and performance are tightly coupled to weld integrity[2]. Despite ongoing technological advances, GMAW joints remain vulnerable to a spectrum of defects-porosity, lack of fusion, cracks, and burn-through-each of which compromises strength, fatigue life, and ultimately the reliability of the finished product[3,4]. Consequently, rigorous defect detection is essential, both for in-line quality assurance and for post-production inspection.

**译文:** GMAW 是现代制造的重要工艺，具有较高生产效率、易于自动化、可稳定获得高质量焊缝等优点[1]。汽车、造船、能源和航空航天等要求结构完整性的行业，用 GMAW 制造安全与性能高度依赖焊缝完整性的关键部件[2]。尽管技术不断进步，GMAW 接头仍可能出现气孔、未熔合、裂纹和烧穿等缺陷。这些缺陷都会损害产品强度、疲劳寿命与最终可靠性[3,4]。因此，严格的缺陷检测对生产线质量保证和焊后检验均不可或缺。

<a id="S008"></a>
**Source**　p.2 · S008

**Original:** Traditionally, defects are identified after welding using non-destructive testing (NDT) techniques such as X-ray or ultrasonic inspection[5–7]. However, post-weld NDT is time-consuming, requires skilled interpretation, and offers no insight into the root cause or immediate process mitigation of defects. The feedback delay means that discontinuities-such as internal voids or incomplete penetration-are discovered only after the weld has finished, often necessitating costly repairs or scrap.

**译文:** 传统上，缺陷在焊后利用 X 射线或超声等无损检测技术识别[5–7]。焊后检测耗时，需要专业判读，也难以说明缺陷的根本成因或支持即时纠偏。反馈延迟意味着内部空洞、未焊透等不连续只能在焊完后发现，常导致昂贵的返修或报废。

<a id="S009"></a>
**Source**　p.2 · S009

**Original:** Delivering immediate defect information to the welding system or operator can dramatically reduce waste and improve productivity[8]. In-process monitoring can support early detection, process adjustment, and more robust manufacturing. The welding process is inherently complex; sensor signals are often noisy, indirect, and highly dynamic. Conventional monitoring has employed a range of sensors: Electrical probes (current/voltage) that are readily available but do not directly capture molten-pool behavior[9], Acoustic emission microphones that can be masked by ambient noise[10,11], Optical vision systems that must contend with intense arc illumination and require careful alignment to view the weld pool[12]. Each modality alone provides an incomplete picture, motivating research into advanced sensing strategies and intelligent data fusion[13].

**译文:** 及时向焊接系统或操作人员反馈缺陷信息，可显著减少浪费并提高生产率[8]。过程内监测有助于早期发现问题、调整工艺和提高制造稳定性。焊接过程复杂，传感信号往往含噪、间接且快速变化。传统监测使用多种传感器。电流和电压探头容易获得，却无法直接观察熔池行为[9]。声发射麦克风会受到环境噪声干扰[10,11]。光学视觉系统面临强烈弧光，需要精确布置才能观察熔池[12]。各模态提供的信息均有限，推动了先进传感和智能数据融合研究[13]。

<a id="S010"></a>
**Source**　p.2 · S010

**Original:** In recent years, deep learning has emerged as a powerful framework for automating defect recognition from both post-weld NDT imagery and in-process sensor streams[14]. Convolutional neural networks (CNNs) and related architectures have surpassed traditional image-processing algorithms in radiographic weld inspections[15], achieving F1-scores above 0.95 on segmentation task[16]. Attention mechanisms have been explored to focus models on defect regions, yielding modest improvements when applied in isolation [17].

**译文:** 近年来，深度学习成为从焊后无损检测图像或过程内传感数据流中自动识别缺陷的重要方法[14]。CNN 及相关架构在焊缝射线检测中超过传统图像处理算法[15]，有分割任务报告 F1 超过 0.95[16]。研究者也用注意力机制让模型聚焦于缺陷区域，单独采用时改进有限[17]。

<a id="S011"></a>
**Source**　p.2 · S011

**Original:** Despite the impressive performance of learning-based approaches in offline NDT, translating these models into in-process defect classifiers remains challenging. The welding process is highly dynamic and nonlinear; a model trained on one material, joint geometry, or set of process parameters often fails to generalize when conditions change[18]. In contrast, the electrical current and arc voltage that every GMAW system already records contain rich, time-varying signatures of arc stability, metal-transfer mode, and heat input-factors that directly govern defect formation[19]. Earlier studies have demonstrated that even simple statistics extracted from these waveforms (e.g., mean, variance, spectral peaks) correlate strongly with bead geometry, penetration depth, and, in some cases, mechanical properties. This makes the electrical signals an attractive, readily available source for in-process monitoring[20]. This establishes a firm foundation for inferring defect conditions purely from electrical pattern recognition. Recent work has taken advantage of one-dimensional convolutional neural networks (1-D CNNs) that ingest raw waveforms (or their short-time Fourier transforms / spectrograms). By learning hierarchical features, such models can discriminate subtle changes that indicate inadequate or excessive penetration. For example, Kim et al. transformed GMAW current and voltage into time–frequency representations and trained a three-layer CNN to classify root-pass penetration status (partial, full, or burn-through) with 97.8 % accuracy[21]. This success underscores the effectiveness of 1-D CNN-based feature extraction from electrical sensor data. The main advantage of this approach is that the signals are available during welding without any extra instrumentation. However, electrical signals alone may miss defects that do not substantially disturb arc behavior, such as surface undercut or visual bead irregularities.

**译文:** 尽管学习方法在离线 NDT 上表现突出，迁移到过程内缺陷分类仍有挑战。焊接高度动态且非线性，基于一种材料、接头几何或参数训练的模型，在条件变化时常难以泛化[18]。GMAW 系统已经记录的电流和电弧电压，包含随时间变化的电弧稳定性、熔滴过渡模式和热输入特征，这些因素直接影响缺陷形成[19]。已有研究发现，即使均值、方差或谱峰等简单描述量，也与焊道几何、熔深乃至某些力学性能密切相关，使电信号成为易获取的监测来源[20]，为仅依靠电信号模式推断缺陷奠定基础。近期研究使用一维 CNN 处理原始波形或其短时傅里叶变换、频谱图，学习分层特征以辨别熔透不足或过度的小变化。Kim 等将电流和电压转成时频表示，用三层 CNN 区分根焊道的部分熔透、完全熔透和烧穿，准确率达 97.8%[21]。该结果支持使用一维 CNN 提取电信号特征。这类信号无需额外仪器即可在焊接中获得，但可能漏掉对电弧扰动较小的表面咬边或焊道外形不规则等缺陷。

<a id="S012"></a>
**Source**　p.2 · S012

**Original:** Parallel to electrical monitoring, molten-pool imaging has become a direct way to observe weld formation [22]. The pool’s size, shape, oscillation, and emissive behavior encode the process state, allowing skilled welders to spot issues such as sudden shrinkage (burn-through) or unusual ripples (lack of fusion). Researchers have deployed optical filters or high-speed cameras to capture clear images under intense arc illumination. CNN-based image classifiers have achieved > 95 % accuracy in identifying penetration state, slag inclusion, and crater defects from single-frame images[23]. Although vision offers intuitive, visual defect cues, it suffers from a highly dynamic surface: a single frame may miss transient events, and high glare or perspective changes introduce substantial noise.

**译文:** 与电信号监测并行，熔池成像成为直接观察焊缝形成的手段[22]。熔池尺寸、形状、振荡和发光行为反映过程状态。熟练焊工可识别突然收缩等烧穿线索，或异常波纹等未熔合线索。研究者用滤光或高速相机在强弧光下采集清晰图像。基于 CNN 的单帧分类在熔透状态、夹渣和弧坑识别中达到超过 95% 的准确率[23]。视觉线索直观，但熔池表面变化快，单帧可能遗漏瞬态事件，强光和视角变化也带来显著噪声。

<a id="S013"></a>
**Source**　p.2 · S013

**Original:** To address the limitations of single-frame imaging, recent studies employ video streams coupled with spatio-temporal CNNs or attention mechanisms. Han et al. introduced a multi-scale feature-fusion framework on molten-pool videos that tracks subtle changes (e.g., light spots from outgassing), achieving ~ 97 % accuracy for porosity detection while handling varying pool sizes and motions [24]. These sophisticated techniques highlight both the promise of molten-pool imaging and the need for robust algorithms that can tolerate glare, perspective shifts, and high visual noise. Moreover, camera-based systems add cost and complexity, motivating careful sensor selection or multimodal fusion.[25]. Combining complementary modalities has proven effective in overcoming the shortcomings of any single sensor. Zeng et al. fused molten-pool images, current, and vibration signals within a feature-selection/ML framework, reporting ≈99 % accuracy for burn-through, pores, and cracks classification[26]. The visual cues clarify ambiguities in the electrical signals, and vice versa, illustrating how multimodal data can resolve defect signatures that would otherwise remain hidden.

**译文:** 为缓解单帧成像局限，近期研究用视频流配合时空 CNN 或注意力机制。文中所述 Han 等提出面向熔池视频的多尺度融合方法，可跟踪逸气产生的光点等细微变化，在不同熔池尺寸和运动下获得约 97% 的气孔检测准确率[24]。这些方法体现了熔池成像的潜力，也表明算法需适应强光、视角变化和高视觉噪声。相机系统增加成本和复杂性，因而需要权衡传感器选择或多模态融合[25]。融合互补模态已被证明能缓解单传感器的局限。Zeng 等将熔池图像、电流和振动信号结合特征选择与机器学习，对烧穿、气孔、裂纹分类报告约 99% 的准确率[26]。视觉和电信号相互补充，可识别单一模态中难以发现的缺陷特征。

<a id="S014"></a>
**Source**　p.2 · S014

**Original:** Recent multimodal fusion research has shifted from simple feature concatenation toward explicit cross-modal interaction. Detail/ scene-guided and difference-correlation-driven fusion methods show that complementary and discrepant information can be selectively preserved across heterogeneous visual modalities[27,28]. Cross-modal attention and co-attention models further demonstrate that adaptive branch interaction is effective for heterogeneous spectroscopy and multi-omics diagnosis[29,30].

**译文:** 近期多模态融合研究从简单特征拼接转向显式跨模态交互。细节与场景引导的融合、基于差异与相关性的融合表明，异质视觉模态间的互补信息和差异信息可以被选择性保留[27,28]。跨模态注意力和协同注意力也表明，自适应分支交互适用于异质光谱与多组学诊断[29,30]。

<a id="S015"></a>
**Source**　p.2 · S015

**Original:** Motivated by these studies, MBGN is positioned as a welding-oriented multimodal fusion framework: synchronized current–voltage waveforms and molten-pool images are not simply concatenated, but are fused through weighted bidirectional feature aggregation and gated cross-modal recalibration.

**译文:** 受这些研究启发，MBGN 被设计为面向焊接的多模态融合框架，通过带权双向特征聚合和跨模态门控重校准融合已同步的电流、电压波形与熔池图像。

<a id="S016"></a>
**Source**　pp.2–3 · S016

**Original:** The novelty of MBGN lies not in introducing a new generic backbone, but in formulating synchronized GMAW monitoring as a cross-scale multimodal signal-processing problem. Specifically, MBGN introduces: (i) timestamp-anchored coupling between 100 ms current–voltage dynamics and the corresponding molten-pool image; (ii) bidirectional multi-scale aggregation to align transient electrical disturbances with spatial weld-pool morphology; and (iii) gated cross-modal recalibration to suppress modality-specific noise and emphasize defect-relevant interactions. This design differs from simple feature concatenation or late fusion by enabling multi-scale interaction before final classification.

**译文:** MBGN 的新意在于将同步的 GMAW 监测建模为跨尺度多模态信号处理问题。具体包括（1）以时间戳为锚，将 100 ms 的电流、电压动态与对应熔池图像配对。（2）以多尺度双向聚合使瞬态电信号扰动与空间熔池形貌相互对应。（3）以跨模态门控重校准抑制模态特异噪声、突出与缺陷相关的交互。该设计在最终分类前就实现多尺度交互，有别于简单特征拼接或后期融合。

<a id="S017"></a>
## 2. 实验

**Source**　p.3 · S017

**Original:** 2. Experimental

**译文:** 2. 实验

<a id="S018"></a>
### 2.1 焊接平台与实验设置

**Source**　p.3 · S018

**Original:** 2.1. Welding platform and experimental setup

**译文:** 2.1 焊接平台与实验设置

<a id="S019"></a>
**Source**　p.3 · S019 · [图 1](#F001)

**Original:** The experiments were carried out on the Midea production line (Fig. 1). A KUKA KR210 × 2 robot positioned a Milwaukee 200-W power source (constant-current mode) to perform 16 fillet-weld seams on Q345R steel plates. Shielding gas was 80 % Ar + 20 % CO2, supplied by a BHP 1000 L/min regulator. The workpiece and filler wire were Q345R (workpiece) and ER70S-6(wire), with wire diameter 1.6 mm.

**译文:** 实验在美的生产线上进行（图 1）。KUKA KR210 × 2 机器人定位 Milwaukee 200-W 电源，电源工作于恒流模式，在 Q345R 钢板上焊制 16 条角焊缝。保护气为 80% Ar + 20% CO₂，由 BHP 1000 L/min 调节器供给。母材为 Q345R，焊丝为直径 1.6 mm 的 ER70S-6。

<a id="F001"></a>
#### 图 1

**首次实质讨论**　[p.3 S019](#S019)  
**原图表页**　p.3 · C001

![图 1](assets/fig01.png)

<a id="C001"></a>
**Original caption:** Fig. 1. Schematic diagram of welding and data acquisition system.

**中文图表标题**　焊接与数据采集系统示意。

**阅读提示**　识别电源、焊接机器人、采集卡和熔池相机之间的信息流。

<a id="S020"></a>
**Source**　p.3 · S020 · [表 1](#T001)

**Original:** Welding parameters varied across the seams to emulate a typical factory environment (Table 1). The robot’s motion controller (KUKA SCARA-6) provided 3-axis positioning at 4–4.2 mm s− 1, while the power source delivered 340–380 A and a constant 32 V arc. The material and joint type were kept consistent, while several plate-thickness and process-parameter groups were included; therefore, the present validation covers limited in-domain process variation rather than cross-material or cross-joint generalization.

**译文:** 为模拟典型工厂环境，各焊缝采用不同参数（表 1）。机器人运动控制器（KUKA SCARA-6）以 4–4.2 mm/s 进行三轴定位，电源提供 340–380 A 电流和恒定 32 V 电弧电压。材料和接头类型保持一致，纳入不同板厚与参数组合。因此，当前验证涵盖有限的域内工艺变化，跨材料或跨接头的泛化仍待验证。

<a id="T001"></a>
#### 表 1

**首次实质讨论**　[p.3 S020](#S020)  
**原图表页**　p.4 · C018

![表 1](assets/table01.png)

<a id="C018"></a>
**Original caption:** Table 1 Welding Parameters of the 16 test seams.

**中文图表标题**　16 条试验焊缝的焊接参数。

**阅读提示**　板厚 6、8、10 mm，焊缝长 1,800–4,000 mm，电流 340–380 A，电压 32 V，焊速 4 或 4.2 mm/s。

<a id="S021"></a>
### 2.2 数据采集

**Source**　p.3 · S021

**Original:** 2.2. Data acquisition

**译文:** 2.2 数据采集

<a id="S022"></a>
**Source**　p.3 · S022

**Original:** A DMT-6000 current sensor (± 500 A range, 100 kHz sampling) and a DMT-5000 voltage sensor (± 100 V range, 100 kHz sampling) were mounted at the welding power source. Their outputs were digitised by a National Instruments cDAQ-9171 (10-bit, 100 kHz).

**译文:** DMT-6000 电流传感器（±500 A，100 kHz）和 DMT-5000 电压传感器（±100 V，100 kHz）安装在焊接电源处，信号由 National Instruments cDAQ-9171 数字化（10 位，100 kHz）。

<a id="S023"></a>
**Source**　p.3 · S023

**Original:** Weld-pool images were captured by a Mecaweld M2-130U monitoring camera at 8 Hz (1280 × 1024 pixels). The camera was positioned 20 cm from the weld pool at a 45◦ angle, equipped with a 2-× telephoto lens and a 700 nm band-pass filter to suppress arc glare.

**译文:** Mecaweld M2-130U 监控相机以 8 Hz 采集 1280 × 1024 像素的熔池图像。相机位于距熔池 20 cm、视角 45° 的位置，配置 2 倍长焦镜头和 700 nm 带通滤光片，以抑制弧光。

<a id="S024"></a>
**Source**　p.3 · S024

**Original:** The industrial control PC (Windows 10, NI LabVIEW 2021) simultaneously issued acquisition start commands to the DAQ and camera at the instant the power source was turned on. An NTP-synchronised timestamp (accuracy < 1 ms) was recorded for every image frame; the DAQ stream was time-stamped by the same PC clock.

**译文:** 工业控制 PC（Windows 10、NI LabVIEW 2021）在焊接电源开启时向 DAQ 和相机同时发出采集启动指令。每帧图像记录经 NTP 同步的时间戳（精度 <1 ms），DAQ 数据流也采用同一 PC 时钟打时间戳。

<a id="S025"></a>
**Source**　p.3 · S025 · [图 2](#F002)

**Original:** For seam LC0250125017, data acquisition started at 12:45:57 UTC and stopped at 13:00:13 UTC (856 s). This produced 8.56 × 108 samples per channel. The raw streams were subsequently segmented into “weld-active” windows by detecting idle periods (current < 30 A) and trimming the arc ignition/extinguishment tails (≈ 200 ms each). Fig. 2 shows the full timeline, segmentation, and a representative down-sampled waveform (5 kHz).

**译文:** 以 LC0250125017 焊缝为例，采集从 UTC 12:45:57 到 13:00:13，持续 856 s。原文称每通道获得 8.56 × 10⁸ 个采样点。随后识别低于 30 A 的空闲时段，并去除引弧和熄弧端各约 200 ms，得到有效焊接窗口。图 2 给出完整时间线、分段及一例降采样到 5 kHz 的波形。

<a id="F002"></a>
#### 图 2

**首次实质讨论**　[p.3 S025](#S025)  
**原图表页**　p.4 · C002

![图 2](assets/fig02.png)

<a id="C002"></a>
**Original caption:** Fig. 2. Acquisition timeline, segmented and down-sampled current–voltage signals.

**中文图表标题**　采集时间线，以及经分段和降采样的电流–电压信号。

**阅读提示**　区分整条采集记录、有效起弧段与降采样展示。图中的 5 kHz 展示波形有别于模型输入的 100 kHz。

<a id="S026"></a>
**Source**　p.3 · S026 · [图 3](#F003)

**Original:** After welding, each seam was inspected by a licensed radiographer using a Nikon 3-axis X-ray system (kV = 140, mA = 5). Radiographs were processed with a YOLOv8-based detector trained on 2 k annotated seam images (four defect classes: slag inclusion, contamination, cracks, undercuts). The detector achieved an mAP@0.5 of 0.87 on a held-out validation set. Detected defects were manually verified by two radiographers; disagreements were resolved by consensus. Fig. 3 shows a radiograph with the final bounding boxes overlaid on the seam.

**译文:** 焊后，由持证射线检测人员用 Nikon 三轴 X 射线设备检验每条焊缝（140 kV、5 mA）。射线图由基于 YOLOv8 的检测器处理。检测器使用 2,000 张标注焊缝图像训练，原文列出的类别为夹渣、污染、裂纹和咬边，留出验证集 mAP@0.5 为 0.87。两名射线检测人员人工复核，分歧经协商解决。图 3 为叠加最终检测框的射线图。

<a id="F003"></a>
#### 图 3

**首次实质讨论**　[p.3 S026](#S026)  
**原图表页**　p.5 · C003

![图 3](assets/fig03.png)

<a id="C003"></a>
**Original caption:** Fig. 3. Examples of defect detection results, indicating weld seams (white bounding boxes) and defects (red bounding boxes).

**中文图表标题**　缺陷检测示例。白框标示焊缝，红框标示缺陷。

**阅读提示**　这些是焊后射线检测结果，用于生成过程样本的标签。

<a id="S027"></a>
**Source**　p.3 · S027 · [图 4](#F004)

**Original:** Weld-pool images contained a cluttered background (e.g., tooling, gas spray). We annotated a subset of 300 images to delineate the weld-pool and arc region. A YOLOv8 detector (mAP = 0.95) was then applied to all 93 570 images. Bounding boxes were enlarged by 50 px to ensure complete coverage, and the cropped sub-images (≈ 640 × 480) were stored for training. Fig. 4 illustrates the cropping workflow.

**译文:** 熔池图像包含工装、气体喷流等复杂背景。作者标注 300 帧以圈定熔池和电弧区域，用 YOLOv8 检测器（mAP = 0.95）处理全部 93,570 帧。检测框扩大 50 px，以便完整覆盖目标，约 640 × 480 的裁剪图用于训练。图 4 展示裁剪流程。

<a id="F004"></a>
#### 图 4

**首次实质讨论**　[p.3 S027](#S027)  
**原图表页**　p.5 · C004

![图 4](assets/fig04.png)

<a id="C004"></a>
**Original caption:** Fig. 4. Examples illustrating the image cropping method based on detected weld-pool and arc regions.

**中文图表标题**　基于检测到的熔池与电弧区域裁剪图像的示例。

**阅读提示**　对照原始视野、检测框和裁剪后的熔池区域。

<a id="S028"></a>
**Source**　pp.3–4 · S028 · [图 5](#F005)

**Original:** For each cropped image, its acquisition timestamp served as an anchor. Using linear interpolation, we extracted a 100 ms window (± 50 ms) of current and voltage data around this anchor, resulting in a 10 k-sample (100 kHz) segment per image. This window was chosen to capture the full arc dynamics associated with the instant the image was taken. At 100 kHz, this 100 ms window corresponds to 10,000 samples and covers short-time arc dynamics around the visual observation, including transient voltage fluctuation, metal-transfer-related disturbance, and local heat-input variation. In this study, weld-pool cropping was performed offline before model training and evaluation (Fig. 5).

**译文:** 每张裁剪图的采集时间戳作为锚点。以线性插值取锚点前后各 50 ms 的电流、电压数据，每帧配对 100 ms、100 kHz 的信号段（10,000 采样点）。此窗口用于捕获该帧附近的短时电弧动态，包括瞬态电压波动、熔滴过渡相关的扰动及局部热输入变化。本文在模型训练和评估前离线裁剪熔池图像（图 5）。

<a id="F005"></a>
#### 图 5

**首次实质讨论**　[pp.3–4 S028](#S028)  
**原图表页**　p.5 · C005

![图 5](assets/fig05.png)

<a id="C005"></a>
**Original caption:** Fig. 5. Schematic diagram of data alignment and labeling.

**中文图表标题**　数据对齐与标注示意。

**阅读提示**　顺着相机帧、同步电信号窗口及 RT 焊缝位置三条信息链看。

<a id="S029"></a>
**Source**　p.4 · S029 · [图 6](#F006)

**Original:** The anchor’s relative position along the seam (normalized ∈ [1]) was mapped to the seam length (mm) to locate the physical weld segment. Defect labels from the radiographic analysis were then assigned to each signal-image pair (Fig. 6).

**译文:** 将锚点在焊缝上的相对位置（原文归一化区间写作 [1]）映射到焊缝物理长度（mm），定位其对应的焊段。随后把射线分析得到的缺陷标签赋给各信号—图像对。原文此处引用图 6。

<a id="S030"></a>
**Source**　p.4 · S030 · [表 2](#T002)、[图 6](#F006)

**Original:** The above procedure yielded 93,570 multimodal samples (image + current segment + voltage segment). The class distribution is shown in Table 2.

**译文:** 上述流程共得到 93,570 组多模态样本，每组含图像、电流段和电压段。类别分布见表 2。

<a id="T002"></a>
#### 表 2

**首次实质讨论**　[p.4 S030](#S030)  
**原图表页**　p.6 · C019

![表 2](assets/table02.png)

<a id="C019"></a>
**Original caption:** Table 2 Class distribution after alignment.

**中文图表标题**　配准后的类别分布。

**阅读提示**　正常 92,584（98.96%），异物 36（0.038%），空洞 7（0.0075%），纵向裂纹 7（0.0075%），咬边 936（1.00%）。

<a id="F006"></a>
#### 图 6

**首次实质讨论**　[p.4 S030](#S030)  
**原图表页**　p.6 · C006

![图 6](assets/fig06.png)

<a id="C006"></a>
**Original caption:** Fig. 6. Pie chart of total data set category distribution.

**中文图表标题**　全数据集类别分布饼图。

**阅读提示**　图注称全数据集，但图内正常 1,180、咬边 936 等数字合计 2,166，与抽样后的监督子集一致。全量配准样本 93,570 的分布见表 2。

<a id="S031"></a>
**Source**　p.4 · S031

**Original:** Because the aligned dataset was dominated by Normal samples, all 986 defect samples were retained, and 1,180 Normal samples were randomly selected in a seam-balanced manner. This produced a supervised subset of 2,166 samples, which was further divided into 1,730 training samples and 436 hold-out evaluation samples. During training, class imbalance was further handled by a class-balanced weighted sampler and class-balanced softmax focal loss. All data processing and model training scripts are implemented in Python 3.10. Core libraries include NumPy 1.26, Pandas 2.1, PyTorch 2.2, OpenCV 4.8, and the Ultralytics YOLOv8 package. Specifically, the same number of Normal samples was selected from each weld seam, with random sampling performed within each seam. During training, class imbalance was further handled by a class-balanced weighted sampler and class-balanced softmax focal loss.

**译文:** 对齐数据中正常样本占绝大多数。作者保留全部 986 个缺陷样本，并按焊缝均衡随机抽取 1,180 个正常样本，共组成 2,166 个监督样本，再划分为 1,730 个训练样本与 436 个留出评估样本。训练使用类别均衡加权采样器与类别均衡 softmax 焦点损失。数据处理和训练脚本采用 Python 3.10，核心库包括 NumPy 1.26、Pandas 2.1、PyTorch 2.2、OpenCV 4.8 和 Ultralytics YOLOv8。具体到正常样本，各焊缝内随机抽样，原文称每条焊缝抽取相同数量。训练阶段继续采用类别均衡加权采样和类别均衡 softmax 焦点损失。

<a id="S032"></a>
**Source**　p.7 · S032

**Original:** Because adjacent samples from continuous welding sequences may be temporally correlated, the data split was designed with caution. Normal samples were randomly selected within each seam while keeping a comparable number of Normal samples across seams, so that the evaluation would not be dominated by a few long Normal sequences. Defect samples were retained according to the RT-derived labels to preserve the rare classes. We note that this held-out split does not constitute a strict leave-one-seam-out validation; such a protocol is currently unsuitable because Hollow and L-crack samples are concentrated in individual seams and would be absent from either training or testing. Therefore, the present evaluation should be interpreted as a held-out assessment under the available long-tailed dataset, while stricter group-level validation will require additional rare-defect data across multiple seams.

**译文:** 连续焊接序列中的相邻样本可能存在时间相关性，作者因此谨慎划分数据。正常样本在各焊缝内随机抽取，且各焊缝的正常样本量相近，以免评估被少数较长的正常序列主导。按照 RT（射线检测）标签保留缺陷样本，以保住稀有类别。当前留出划分没有采用严格的逐条焊缝留一验证。空洞和纵向裂纹集中在个别焊缝，严格留一会使这些类别从训练集或测试集消失。因此，当前结果应理解为现有长尾数据上的留出评估，严格的按组验证仍需在多条焊缝上补充稀有缺陷样本。

<a id="S033"></a>
### 2.3 网络架构

**Source**　p.7 · S033

**Original:** 2.3. Network architecture

**译文:** 2.3 网络架构

<a id="S034"></a>
**Source**　p.7 · S034 · [图 7](#F007)

**Original:** A Multi-modal BiFPN Gate Network (MBGN), which is a multimodal deep-learning framework specifically designed for welding-defect classification, is introduced. MBGN comprises four synergistic components: (1) a 1-D convolutional neural network (1-D-CNN) for temporal feature extraction from current-voltage signals; (2) a ResNet-based visual encoder for spatial feature extraction from weld-pool images; (3) a Bidirectional Feature Pyramid Network (BiFPN) that fuses multi-scale features from both modalities; and (4) a cross-attention Gate that adaptively recalibrates the fused representation. Fig. 7 shows the complete architecture. The methodological focus is the welding-specific cross-modal interaction between electrical arc dynamics and molten-pool morphology, rather than only the reuse of generic backbone components.

**译文:** 本文提出专门用于焊接缺陷分类的多模态深度学习框架 MBGN。它包含四个协同模块。（1）一维 CNN 从电流、电压信号中提取时间特征。（2）ResNet 视觉编码器从熔池图像中提取空间特征。（3）双向特征金字塔网络（BiFPN）融合两模态的多尺度特征。（4）交叉注意力门控自适应重校准融合表示。图 7 给出完整架构。设计重点是让电弧电信号动态与熔池形貌在焊接任务中实现跨模态交互。

<a id="F007"></a>
#### 图 7

**首次实质讨论**　[p.7 S034](#S034)  
**原图表页**　p.6 · C007

![图 7](assets/fig07.png)

<a id="C007"></a>
**Original caption:** Fig. 7. MBGN overall network architecture diagram.

**中文图表标题**　MBGN 总体网络架构。

**阅读提示**　从左至右追踪双分支编码、双向聚合、交叉注意力门控与分类输出。图中画出 P1–P4，方法正文给出的实现公式使用 P3 和 P4，复现前宜核对代码。

<a id="S035"></a>
### 2.3.1 一维卷积神经网络模块（1D-CNN）

**Source**　p.7 · S035

**Original:** 2.3.1. One-dimensional convolutional neural network (1D-CNN) module

**译文:** 2.3.1 一维卷积神经网络模块（1D-CNN）

<a id="S036"></a>
**Source**　p.7 · S036 · [图 8](#F008)

**Original:** The electrical branch uses a compact residual 1-D CNN to encode the 100 ms current–voltage segment. Dilated convolutions with rates 1, 2, 4, and 8 expand the temporal receptive field without a large parameter increase, allowing the branch to capture both short arc-instability events and slower process trends. The network diagram is shown in Fig. 8.

**译文:** 电信号分支通过紧凑的残差一维 CNN 编码 100 ms 电流—电压片段。扩张率为 1、2、4 和 8 的卷积在参数量增加较少的情况下扩大时间感受野，从而捕获短暂的电弧失稳及较慢的过程趋势。图 8 为网络示意。

<a id="F008"></a>
#### 图 8

**首次实质讨论**　[p.7 S036](#S036)  
**原图表页**　p.7 · C008

![图 8](assets/fig08.png)

<a id="C008"></a>
**Original caption:** Fig. 8. Network architecture diagram of 1D-CNN module.

**中文图表标题**　一维 CNN 模块架构。

**阅读提示**　关注扩张卷积的时间感受野、残差结构和送入融合模块的层级。

<a id="S037"></a>
### 2.3.2 基于 ResNet 的视觉编码器

**Source**　p.7 · S037

**Original:** 2.3.2. ResNet-based visual encoder

**译文:** 2.3.2 基于 ResNet 的视觉编码器

<a id="S038"></a>
**Source**　p.7 · S038

**Original:** The visual branch adopts a ResNet-18 backbone pretrained on ImageNet and fine-tuned on the cropped molten-pool images. It extracts spatial features related to weld-pool shape, arc-brightness distribution, bead-edge continuity, and local texture variation. The resulting visual embeddings are fused with electrical features in the subsequent BiFPN module.

**译文:** 视觉分支采用在 ImageNet 上预训练的 ResNet-18，并在裁剪后的熔池图像上微调。它提取与熔池形状、弧光亮度分布、焊道边缘连续性以及局部纹理变化有关的空间特征。视觉嵌入随后在 BiFPN 中与电信号特征融合。

<a id="S039"></a>
### 2.3.3 双向特征金字塔网络

**Source**　p.7 · S039

**Original:** 2.3.3. Bidirectional feature pyramid network

**译文:** 2.3.3 双向特征金字塔网络

<a id="S040"></a>
**Source**　p.7 · S040

**Original:** The BiFPN module fuses multi-scale electrical and visual features through learnable weighted aggregation in both top-down and bottom-up directions. In MBGN, high-level features from both branches are projected into a shared 256-dimensional space, fused at corresponding stages, and then aggregated through the bidirectional weighted paths. This design preserves cross-modal interaction before classification while avoiding a heavy fusion head.

**译文:** BiFPN 通过自上而下和自下而上的可学习加权聚合，融合多尺度电信号与视觉特征。MBGN 把两分支的高层特征投影到共同的 256 维空间，在对应阶段融合，再沿双向带权路径聚合。该设计在分类前实现跨模态交互，融合头的计算量也较轻。

<a id="S041"></a>
**Source**　p.7 · S041

**Original:**

```text
Let Sl and Vl denote the electrical-signal feature and the visual feature at scale l, respectively. In the implemented MBGN, the BiFPN
module uses the two high-level scales l ∈ {3, 4}. The features from the two modalities are first projected into a shared feature space:
                (    (     ))          (     (     ))
       S l = LN SiLU Wls Sl , V
       ̂                       ̂ l = LN SiLU Wv Vl
                                                 l
```

**译文:** 设 $S_l$ 和 $V_l$ 分别表示尺度 $l$ 的电信号和视觉特征。MBGN 的 BiFPN 采用两个高层尺度 $l\in\{3,4\}$。首先将两种模态投影到共同特征空间。

$$\hat S_l=\mathrm{LN}(\mathrm{SiLU}(W_l^s S_l)),\qquad \hat V_l=\mathrm{LN}(\mathrm{SiLU}(W_l^v V_l)).$$

<a id="S042"></a>
**Source**　pp.7–8 · S042

**Original:**

```text
The same-scale cross-modal feature is then obtained as:
Pl = Φl ([ ̂
                    Sl ; V
                         ̂ l ] ), l∊{3, 4}
where [•; •] denotes feature concatenation, and Φl ( • ) represents a linear projection followed by SiLU activation and a residual feed-
forward block.
```

**译文:** 同尺度跨模态特征为 $P_l=\Phi_l([\hat S_l;\hat V_l]),\ l\in\{3,4\}$。其中 $[\cdot;\cdot]$ 表示特征拼接，$\Phi_l$ 表示线性投影，再接 SiLU 激活和残差前馈块。

<a id="S043"></a>
**Source**　p.8 · S043

**Original:**

```text
The normalized weighted aggregation used in BiFPN can be expressed as:
                             n
                             ∑          ReLU(wi )
         WA(X1 , ⋯, Xn ) =         ∑n       ( )    Xi
                             i=1     j=1 ReLUwj + ∊
```

**译文:** BiFPN 使用的归一化加权聚合为

$$\mathrm{WA}(X_1,\ldots,X_n)=\sum_{i=1}^n\frac{\mathrm{ReLU}(w_i)}{\sum_{j=1}^n\mathrm{ReLU}(w_j)+\epsilon}X_i.$$

<a id="S044"></a>
**Source**　p.8 · S044

**Original:**

```text
Accordingly, the top-down and bottom-up aggregation in MBGN is formulated as:T4 = P4
         T3 = WA(P3 , U(T4 ))
B4 = WA(T4 , D(T3 ), P4 )
FBiFPN = T3 + B4
where U( • ) and D( • ) denote learnable top-down and bottom-up feature transformations, respectively.
```

**译文:** MBGN 的自上而下与自下而上聚合可写为

$$T_4=P_4,\quad T_3=\mathrm{WA}(P_3,U(T_4)),\quad B_4=\mathrm{WA}(T_4,D(T_3),P_4),\quad F_{\mathrm{BiFPN}}=T_3+B_4.$$

$U$ 和 $D$ 分别是可学习的自上而下及自下而上特征变换。

<a id="S045"></a>
**Source**　p.8 · S045

**Original:**

```text
For clarity, the previous no-BiFPN ablation is renamed MWFN (Multimodal Weighted-Fusion Network). MWFN first aggregates
multi-scale features within each modality using learnable weighted addition and then directly adds the electrical and visual vectors
before classification; it therefore tests weighted late fusion without bidirectional cross-modal aggregation:
FMWFN = WA( ̂
                     S3, ̂
                         S 4 ) + WA( V
                                     ̂ 3, V
                                          ̂ 4)
```

**译文:** 作者将原先去除 BiFPN 的消融模型命名为 MWFN（多模态加权融合网络）。它先对各模态内部的多尺度特征做可学习的加权加法，再将电信号向量与视觉向量直接相加后分类。这个对照考察省去跨模态双向聚合的加权后期融合。

$$F_{\mathrm{MWFN}}=\mathrm{WA}(\hat S_3,\hat S_4)+\mathrm{WA}(\hat V_3,\hat V_4).$$

<a id="S046"></a>
### 2.3.4 交叉注意力门控

**Source**　p.8 · S046

**Original:** 2.3.4. Cross attention gate

**译文:** 2.3.4 交叉注意力门控

<a id="S047"></a>
**Source**　p.8 · S047

**Original:**

```text
The Gate module implements a multi-head cross-attention mechanism that explicitly models inter-modal dependencies. Given a
temporal query vector Q from the 1-D-CNN and visual key/value vectors K,V from ResNet, the module computes:
                                ( T)
                                 QK
       Attention(Q, K) = Softmax √̅̅̅̅
                                   D
```

**译文:** Gate 通过多头交叉注意力显式建模模态间依赖。一维 CNN 提供时间查询向量 $Q$，ResNet 提供视觉键和值向量 $K,V$。门控首先计算

$$\mathrm{Attention}(Q,K)=\mathrm{Softmax}(QK^\mathsf{T}/\sqrt{D}).$$

<a id="S048"></a>
**Source**　p.8 · S048

**Original:**

```text
where D is the embedding dimension. Subsequently, we obtain the recalibrated gating vector G by weighting the visual values V′:
G = σ(Attention(Q, K) • Vʹ )
```

**译文:** $D$ 是嵌入维数。随后对视觉值 $V'$ 加权得到重校准门控向量 $G=\sigma(\mathrm{Attention}(Q,K)\cdot V')$。

<a id="S049"></a>
**Source**　p.8 · S049

**Original:**

```text
Here, σ denotes the sigmoid activation function, ensuring the gating values remain between 0 and 1. The final recalibrated feature
vector Tʹ is computed as channel-wise multiplication of the temporal feature and gating vector:
Tʹ = T ⊙ G
```

**译文:** $\sigma$ 为 sigmoid 激活，将门控值限制在 0 至 1。用时间特征与门控向量按通道相乘，得到重校准特征 $T'=T\odot G$。

<a id="S050"></a>
**Source**　p.8 · S050

**Original:** Multi-head attention allows the network to capture diverse correlations between the two modalities, enhancing the discriminative power for subtle defects.

**译文:** 多头注意力使网络能捕获两种模态之间的多样相关性，提高对细微缺陷的辨别能力。

<a id="S051"></a>
### 2.3.5 训练方案

**Source**　p.8 · S051

**Original:** 2.3.5. Training protocol

**译文:** 2.3.5 训练方案

<a id="S052"></a>
**Source**　p.8 · S052

**Original:** The network is trained end-to-end using class-balanced softmax focal loss and a class-balanced weighted sampler. The training set contains 2,166 labeled samples from 16 production weld seams, including 1,180 Normal samples and 986 defect samples; the remaining 91,404 aligned but unlabeled samples are reserved for future semi-supervised or weakly supervised studies.

**译文:** 网络使用类别均衡 softmax 焦点损失和类别均衡加权采样器进行端到端训练。本段称来自 16 条生产焊缝的“训练集”含 2,166 个带标签样本，其中 1,180 个正常、986 个有缺陷。其余 91,404 个已配准但未标注样本留待半监督或弱监督研究。关于 2,166 的口径，见第 4 页的监督子集划分与末尾核对说明。

<a id="S053"></a>
### 2.4 实现细节

**Source**　p.9 · S053

**Original:** 2.4. Implementation details

**译文:** 2.4 实现细节

<a id="S054"></a>
**Source**　p.9 · S054 · [表 3](#T003)

**Original:** MBGN was trained on the multimodal dataset described in Section 2.2 and compared with representative one-dimensional, image-based, and multimodal baselines. The 1-D baselines include LSTM and MSTCN; the image baselines include ResNet variants and MambaOut-femto; and MWFN evaluates weighted late fusion without bidirectional cross-modal aggregation. All experiments were implemented in PyTorch 2.2 on a workstation with an NVIDIA RTX 3060 GPU and an Intel i7-12700 K CPU. Unless otherwise stated, the main training hyperparameters are listed in Table 3.

**译文:** MBGN 使用第 2.2 节的多模态数据集训练，并与代表性的一维、图像和多模态基线比较。一维基线为 LSTM 和 MSTCN，图像基线为 ResNet 系列与 MambaOut-femto，MWFN 用于评估省去跨模态双向聚合的加权后期融合。实验以 PyTorch 2.2 实现，在 NVIDIA RTX 3060 GPU 和 Intel i7-12700 K CPU 工作站上运行。除另有说明，主要超参数见表 3。

<a id="T003"></a>
#### 表 3

**首次实质讨论**　[p.9 S054](#S054)  
**原图表页**　p.8 · C020

![表 3](assets/table03.png)

<a id="C020"></a>
**Original caption:** Table 3 Network training related parameters.

**中文图表标题**　网络训练参数。

**阅读提示**　图像边长 224，序列长度 10,000，批量 64，训练 300 个 epoch。基础/最大学习率 3e-4/4e-3。预热占比 0.1，EMA 0.9995，梯度裁剪 5.0，CutMix 概率 0.2，辅助损失权重 0.2，早停耐心值 120。损失与采样均采用类别均衡策略。

<a id="S055"></a>
**Source**　p.9 · S055

**Original:** Training used a 10% learning-rate warm-up, EMA parameter averaging with a decay of 0.9995, gradient clipping with a norm of 5, and 1-D CutMix augmentation with a maximum probability of 0.2. An auxiliary loss with weight 0.2 was applied to the sequence and image auxiliary heads.

**译文:** 训练使用 10% 的学习率预热、衰减系数为 0.9995 的指数移动平均（EMA）、范数为 5 的梯度裁剪，以及最大概率 0.2 的一维 CutMix 增强。序列与图像辅助分类头的损失权重为 0.2。

<a id="S056"></a>
**Source**　p.9 · S056 · [表 4](#T004)

**Original:** Table 4 summarizes the parameter count, inference speed, and floating-point operations per forward pass for the six networks. MBGN, while slightly larger than MSTCN, remains computationally lightweight, achieving 4.28 ms per sample (≈ 233 FPS) with 2.68 GFLOPs. This measured value refers only to isolated forward inference after offline image cropping and signal-window alignment. Because the camera operates at 8 Hz, image acquisition is bounded by a 125 ms frame interval, and the centered 100 ms signal window requires approximately 50 ms of waiting after each image timestamp. Cropping, synchronization, interpolation, and I/O were not measured in a fully integrated online pipeline. Therefore, the timing result supports the computational feasibility of MBGN for in-process monitoring, while full sensor-to-decision latency still requires production-line validation.

**译文:** 表 4 汇总了六个网络的参数量、推理速度和单次前向传播的浮点运算量。MBGN 比 MSTCN 大一些，单样本计算耗时 4.28 ms（约 233 FPS），运算量为 2.68 GFLOPs。此时间来自离线完成图像裁剪和信号窗口对齐后的独立前向推理。8 Hz 相机的帧间隔为 125 ms，以图像为中心的 100 ms 信号窗口还要求在帧时间戳后等待约 50 ms。裁剪、同步、插值及 I/O 尚未在完整在线流程中计时。结果说明过程内运行在模型计算层面可行，完整的传感到决策延迟仍需上产线验证。

<a id="T004"></a>
#### 表 4

**首次实质讨论**　[p.9 S056](#S056)  
**原图表页**　p.9 · C021

![表 4](assets/table04.png)

<a id="C021"></a>
**Original caption:** Table 4 Comparison of network performance of six models.

**中文图表标题**　六个模型的网络性能比较。

**阅读提示**　MBGN 参数量 13.76 M，单样本耗时 4.28 ms，约 233.60 FPS，单次前向运算 2.68 GFLOPs。

<a id="S057"></a>
**Source**　p.9 · S057

**Original:**

```text
Two complementary metrics were used:
                            TP + TN
          Accuracy =
                       TP + FP + TN + FN
where TP, TN, FP, and FN represent true positives, true negatives, false positives, and false negatives, respectively.
                             Precision × Recall
          F1 − score = 2 ×
                             Precision + Recall
                     TP              TP
where Precision = TP+FP , Recall = TP+FN 。Together, these metrics offer a comprehensive assessment of classification performance,
particularly under imbalanced data distributions.
```

**译文:** 采用两个互补指标。准确率 $\mathrm{Accuracy}=(TP+TN)/(TP+FP+TN+FN)$，其中 $TP,TN,FP,FN$ 分别为真阳性、真阴性、假阳性、假阴性。$F_1=2\mathrm{Precision}\times\mathrm{Recall}/(\mathrm{Precision}+\mathrm{Recall})$，其中 $\mathrm{Precision}=TP/(TP+FP)$，$\mathrm{Recall}=TP/(TP+FN)$。两个指标结合用于评估分类性能，尤其适用于类别不均衡的情况。

<a id="S058"></a>
### 2.5 特征相关性分析

**Source**　p.9 · S058

**Original:** 2.5. Characteristic correlation analysis

**译文:** 2.5 特征相关性分析

<a id="S059"></a>
**Source**　p.9 · S059

**Original:** After MBGN training, we correlated handcrafted time-domain, frequency-domain, and time–frequency-domain descriptors of the electrical signals with intermediate features extracted from the best MBGN model. The purpose was to identify which physical signal attributes were most strongly associated with the learned representations under different defect conditions.

**译文:** 训练完成后，作者将电信号的手工时域、频域和时频域描述量与最优 MBGN 模型的中间特征做相关分析，目的是识别在不同缺陷条件下与学习表示关联最强的物理信号属性。

<a id="S060"></a>
**Source**　p.9 · S060

**Original:** The handcrafted descriptors were grouped into three families. Time-domain features summarize signal amplitude, pulse characteristics, dynamic resistance, arc power, crest factors, and heat-input-related quantities. Frequency-domain features describe FFT/PSD-based spectral shape, dominant frequency, and band-limited energies. Time-frequency features use short-time band energies of current and voltage in predefined bands from 0-200 Hz to 30–50 kHz to capture transient spectral patterns related to arc stability and pulsing behavior. Pearson correlation and the Maximal Information Coefficient (MIC) were then used to examine linear and nonlinear associations between these descriptors and the stage-wise MBGN features obtained by mean and max pooling.

**译文:** 手工描述量分三类。时域特征描述幅值、脉冲特性、动态电阻、电弧功率、峰值因子及热输入相关量。频域特征以 FFT 或 PSD 描述谱形、主频和各频带能量。时频特征使用电流和电压在 0–200 Hz 至 30–50 kHz 等预设频带的短时能量，捕获与电弧稳定性和脉冲行为相关的瞬态频谱模式。随后用 Pearson 相关和最大信息系数（MIC），研究这些描述量与经均值池化和最大池化得到的各阶段 MBGN 特征之间的线性及非线性联系。

<a id="S061"></a>
## 3. 结果与讨论

**Source**　p.9 · S061

**Original:** 3. Results and discussion

**译文:** 3. 结果与讨论

<a id="S062"></a>
### 3.1 模型训练结果分析

**Source**　p.9 · S062

**Original:** 3.1. Model training results analysis

**译文:** 3.1 模型训练结果分析

<a id="S063"></a>
**Source**　p.9 · S063 · [表 5](#T005)

**Original:** After training the six models for 300 epochs, we evaluated their performance on the held-out test set. Table 5 lists the overall accuracy and macro-averaged F1-score for each network. Although several models show comparable accuracy (approximately 65–74%), this is partly due to the long-tailed test distribution, in which most samples belong to the Normal or Undercut classes. Macro- F1 therefore provides a more informative comparison and shows the advantage of the multimodal design.

**译文:** 六个模型各训练 300 个 epoch 后，在留出测试集上评估。表 5 列出各网络的总体准确率与宏平均 F1。若干模型的准确率相近（原文约 65–74%），部分原因在于测试集是长尾分布，多数样本为正常或咬边。宏平均 F1 能提供更有信息量的比较，并显示多模态设计的优势。

<a id="T005"></a>
#### 表 5

**首次实质讨论**　[p.9 S063](#S063)  
**原图表页**　p.10 · C022

![表 5](assets/table05.png)

<a id="C022"></a>
**Original caption:** Table 5 Comparison of classification performance of six models.

**中文图表标题**　六个模型的分类性能比较。

**阅读提示**　主结果 MBGN 的准确率为 0.748，宏平均 F1 为 0.719。MSTCN 的 F1 为 0.327，ResNet-50 为 0.383。

<a id="S064"></a>
**Source**　pp.9–11 · S064 · [图 9](#F009)

**Original:** Among the classification models for one-dimensional data and those for two-dimensional image data, we selected the models with the best performance based on F1-score, which are MSTCN and ResNet-50 respectively, together with our MBGN network, we compared their model performance using confusion matrices. Fig. 9 displays the confusion matrices of the three models at the epoch with the highest validation macro-F1. MBGN correctly predicts all four defect types and misclassifies only a handful of Normal samples as Undercut. In contrast, the classification models trained solely on a single type of data are completely unable to correctly identify the two types of defects: Hollow and L-crack. Moreover, they are inferior to the multi-modal data-based MBGN in classifying the other three types of defects. Because Hollow and L-crack contain very few evaluation samples, their class-level metrics should be interpreted as preliminary rather than statistically conclusive.

**译文:** 作者分别按 F1 选出一维模型 MSTCN 和二维图像模型 ResNet-50，并与 MBGN 比较混淆矩阵。图 9 给出三者在验证集宏平均 F1 最高的 epoch 的混淆矩阵。MBGN 在四类缺陷中均有正确预测，一些正常样本被误判为咬边。仅用单一数据模态的模型未能正确识别空洞和纵向裂纹，对其余三类样本的分类也弱于 MBGN。空洞和纵向裂纹的评估样本极少，相关类别指标只能作初步参考。

<a id="F009"></a>
#### 图 9

**首次实质讨论**　[pp.9–11 S064](#S064)  
**原图表页**　p.10 · C009

![图 9](assets/fig09.png)

<a id="C009"></a>
**Original caption:** Fig. 9. Confusion matrix of three optimal network models on verification set.

**中文图表标题**　验证集上三个最优网络的混淆矩阵。

**阅读提示**　横轴为真实标签、纵轴为预测标签。MBGN 对角线共 326/436；有 59 个正常样本判成咬边，47 个咬边样本判成正常。空洞与纵向裂纹均为 1/2 命中。

<a id="S065"></a>
**Source**　p.11 · S065 · [表 6](#T006)

**Original:** Table 6 provides the per-class metrics for each model. MBGN achieves the optimal results in all classification metrics for each defect category, including precision, recall, and F1-score. Macro-F1 is emphasized because it gives equal weight to minority classes under the long-tail distribution.

**译文:** 表 6 给出逐类指标。原文称 MBGN 在各缺陷类别的精确率、召回率及 F1 上取得最优结果。宏平均 F1 给每个类别同等权重，适用于长尾分布。此处概括与表内个别数据有出入，见末尾核对说明。

<a id="T006"></a>
#### 表 6

**首次实质讨论**　[p.11 S065](#S065)  
**原图表页**　p.10 · C023

![表 6](assets/table06.png)

<a id="C023"></a>
**Original caption:** Table 6 Comparison of classification performance of three models under different categories.

**中文图表标题**　三个模型的逐类别分类性能比较。

**阅读提示**　每个模型列精确率、召回率及 F1。MBGN 的异物、空洞、纵向裂纹、正常、咬边 F1 依次是 0.941、0.500、0.667、0.767、0.720。

<a id="S066"></a>
### 3.2 统计可靠性分析

**Source**　p.11 · S066

**Original:** 3.2. Statistical reliability analysis

**译文:** 3.2 统计可靠性分析

<a id="S067"></a>
**Source**　p.11 · S067 · [表 7](#T007)

**Original:** To address the statistical reliability of the long-tailed validation results, an additional analysis was conducted for MBGN. First, the predictions on the held-out validation set were resampled by bootstrap with 10,000 iterations to estimate 95% confidence intervals for the overall and class-level metrics. As summarized in Table 7, MBGN achieved an accuracy of 0.736 (95% CI: 0.695–0.778) and a macro-F1 of 0.714 (95% CI: 0.466–0.856).

**译文:** 为评估长尾验证结果的统计可靠性，作者追加分析。首先，对留出验证集的预测做 10,000 次 bootstrap 重采样，估计总体和逐类指标的 95% 置信区间。表 7 给出准确率 0.736（95% CI 0.695–0.778），宏平均 F1 为 0.714（95% CI 0.466–0.856）。

<a id="T007"></a>
#### 表 7

**首次实质讨论**　[p.11 S067](#S067)  
**原图表页**　p.11 · C024

![表 7](assets/table07.png)

<a id="C024"></a>
**Original caption:** Table 7 Statistical reliability of MBGN based on bootstrap confidence intervals and repeated-seed training.

**中文图表标题**　基于 bootstrap 置信区间和重复随机种子训练的 MBGN 统计可靠性。

**阅读提示**　本表使用 bootstrap 点估计和区间。宏平均 F1 0.714，95% CI 0.466–0.856。随机种子的结果另见图 10。

<a id="S068"></a>
**Source**　p.11 · S068

**Original:** The class-level bootstrap results follow the underlying sample distribution. Normal and Undercut, which account for most evaluation samples, show comparatively compact F1-score intervals. Foreign_object also shows strong performance, but its interval is wider because the validation support is limited. In contrast, Hollow and L-crack have the widest uncertainty ranges because each contains only two validation samples. These results indicate that the overall MBGN performance is reproducible at the dataset level, whereas the class-level conclusions for the rarest defects should still be interpreted cautiously.

**译文:** 逐类 bootstrap 结果与样本分布相符。正常和咬边占评估样本多数，F1 区间相对窄。异物性能较强，但验证样本较少，区间较宽。空洞和纵向裂纹各仅两个验证样本，区间最宽。因此，作者认为整体性能在当前数据集层面具有一定可重复性，最稀有类别的结论仍需谨慎。

<a id="S069"></a>
**Source**　p.11 · S069 · [图 10](#F010)

**Original:** Second, three independent training runs were conducted with different random seeds to evaluate whether the result depended on a single favorable initialization. As shown in Fig. 10, the best validation macro-F1 values of the three runs remain close to each other, with 0.749 ± 0.018, and the corresponding accuracy is 0.732 ± 0.021. This small cross-seed variation supports the stability of MBGN under the present training setting, while the rare-class uncertainty noted above remains constrained by the available sample counts.

**译文:** 其次，以三个不同随机种子独立训练，以检验结果是否依赖某次有利初始化。图 10 中，三次最佳验证宏平均 F1 较接近，为 0.749 ± 0.018，对应准确率为 0.732 ± 0.021。跨种子波动较小说明当前训练设置下结果相对稳定，稀有类别的不确定性仍受样本数限制。

<a id="F010"></a>
#### 图 10

**首次实质讨论**　[p.11 S069](#S069)  
**原图表页**　p.12 · C010

![图 10](assets/fig10.png)

<a id="C010"></a>
**Original caption:** Fig. 10. Stability of MBGN performance under three random seeds.

**中文图表标题**　三个随机种子下 MBGN 的性能稳定性。

**阅读提示**　三次训练所用随机种子不同，数据来源和验证协议相同。

<a id="S070"></a>
### 3.3 类别不平衡策略分析

**Source**　p.11 · S070

**Original:** 3.3. Class-imbalance strategy analysis

**译文:** 3.3 类别不平衡策略分析

<a id="S071"></a>
**Source**　p.11 · S071 · [表 8](#T008)

**Original:** To further evaluate the influence of class-imbalance handling, four training strategies were compared using the same proposed MBGN architecture, data split, random seed, and 150-epoch training schedule. E1 used random shuffle with cross-entropy loss, E2 used a class-balanced weighted sampler with cross-entropy loss, E3 used random shuffle with class-balanced focal loss, and E4 used both the weighted sampler and class-balanced focal loss. E4 corresponds to the final MBGN training strategy adopted in this study (Table 8).

**译文:** 保持 MBGN 架构、数据划分、随机种子和 150 个 epoch 的训练方案不变，对比四种不平衡处理策略。E1 使用随机打乱和交叉熵，E2 使用类别均衡加权采样与交叉熵，E3 使用随机打乱与类别均衡焦点损失，E4 同时使用均衡加权采样和类别均衡焦点损失。最终 MBGN 采用 E4（表 8）。

<a id="T008"></a>
#### 表 8

**首次实质讨论**　[p.11 S071](#S071)  
**原图表页**　p.12 · C025

![表 8](assets/table08.png)

<a id="C025"></a>
**Original caption:** Table 8 Best-validation accuracy and macro-F1 under different imbalance-handling strategies.

**中文图表标题**　不同类别不平衡处理策略的最佳验证准确率与宏平均 F1。

**阅读提示**　E4 组合加权采样和 CB-Focal，在此消融组内达到最高准确率 0.7661 和宏平均 F1 0.7495。

<a id="S072"></a>
**Source**　p.11 · S072

**Original:** The best-validation results show that the final MBGN setting (E4) achieves the highest accuracy (0.766) and macro-F1 (0.750), indicating that combining class-balanced sampling and class-balanced focal loss provides the most effective overall strategy for the long-tailed dataset. In contrast, class-balanced focal loss alone does not improve the model when the mini-batch distribution remains imbalanced, suggesting that balanced sampling is essential in the present dataset. Because Hollow and L-crack contain very few validation samples, this analysis is interpreted mainly at the overall macro-F1 level rather than as conclusive evidence for each rare defect class. These values are the best-validation metrics recorded during the same 150-epoch model-selection protocol and are used only for within-ablation comparison of imbalance-handling strategies; they are not intended to replace the final MBGN performance reported in the main comparison table.

**译文:** 最佳验证结果表明最终策略 E4 的准确率（0.766）和宏平均 F1（0.750）最高。均衡采样和类别均衡焦点损失结合，在这组长尾数据上整体效果最好。小批次分布仍然不均衡时，仅引入类别均衡焦点损失没有改善结果，作者据此认为均衡采样在当前数据中很重要。由于空洞与纵向裂纹的验证样本极少，该实验主要依据整体宏平均 F1 解读。这里的结果均为同一 150 epoch 模型选择方案下的最佳验证指标，仅用于这组策略消融的内部比较。

<a id="S073"></a>
### 3.4 模态贡献与视觉采集可靠性

**Source**　p.11 · S073

**Original:** 3.4. Modality contribution and visual-acquisition reliability analysis

**译文:** 3.4 模态贡献与视觉采集可靠性

<a id="S074"></a>
**Source**　p.11 · S074 · [表 9](#T009)

**Original:** The necessity of multimodal sensing was evaluated through independently trained single-modality baselines rather than by artificially disabling one input branch in a trained fusion network. The latter operation may create feature combinations outside the distribution learned by the fusion module and is therefore less suitable for quantifying the intrinsic contribution of each modality. In the baseline comparison, the electrical-signal-only 1DCNN-cls and image-only ResNet-18-cls achieved F1-scores of 0.294 and 0.453, respectively, whereas the proposed MBGN achieved an F1-score of 0.719. This improvement indicates that electrical signals and molten-pool images provide complementary information for balanced defect recognition under the severe class imbalance of the present dataset (Table 9).

**译文:** 作者通过独立训练的单模态基线评估使用多模态传感的必要性。直接禁用已训练融合网络的某输入分支，可能产生超出融合模块训练分布的特征组合，较难量化各模态的本征贡献。仅用电信号的一维 CNN 分类器和仅用图像的 ResNet-18 分类器，F1 分别为 0.294 和 0.453，MBGN 则为 0.719。作者认为电信号与熔池图像在重度类别不平衡的条件下可提供互补信息。原文在此引用表 9，基线数据实际见表 10。

<a id="S075"></a>
**Source**　pp.11–12–13 · S075 · [表 9](#T009)

**Original:** To further address deployment-oriented reliability, the trained MBGN checkpoint was evaluated under visual acquisition degradation and camera-failure scenarios without retraining. This supplementary experiment was motivated by practical GMAW production conditions, where the visual stream can be disturbed during acquisition by arc-glare fluctuations, molten-metal spatter, fumes, and lens contamination. The clean input achieved an accuracy of 0.755 and a macro-F1 of 0.755. Moderate brightness variation caused limited-to-moderate degradation, with macro-F1 values of 0.590 for brightness x0.8 and 0.694 for brightness x1.2. Image noise and blur produced stronger effects: image Gaussian noise reduced macro-F1 to 0.458 (std = 0.03) and 0.199 (std = 0.06), while Gaussian blur produced macro-F1 values of 0.615 (radius = 1) and 0.469 (radius = 2). The missing-image condition reduced macro-F1 to 0.140. The false-positive/false-negative analysis further showed that the clean input had a false-alarm rate of 26.3% and a missed-defect rate of 22.5%, whereas severe image noise (std = 0.06) increased the missed-defect rate to 80.5%, and missing visual input led to complete missed detection of defect samples. These stress tests do not by themselves establish deployment readiness; rather, they identify image quality, camera status, and plant-level validation as necessary safeguards before the model can be considered for closed-loop quality-control use.

**译文:** 为进一步考虑实际部署，作者不重新训练，直接在视觉退化和相机失效情形下评估已训练的 MBGN 检查点。生产中的弧光波动、金属飞溅、烟尘和镜头污染均会干扰图像采集。干净输入的准确率和宏平均 F1 均为 0.755。亮度乘 0.8 或 1.2 后，宏平均 F1 为 0.590、0.694。高斯图像噪声使其降至 0.458（标准差 0.03）或 0.199（标准差 0.06）。高斯模糊使其降至 0.615（半径 1）或 0.469（半径 2）。缺图时宏平均 F1 为 0.140。干净输入的误报率和缺陷漏检率为 26.3% 和 22.5%。严重图像噪声使漏检率升至 80.5%，缺图时所有缺陷样本均漏检。该压力测试指出，考虑闭环质控前应监控图像质量和相机状态，并在生产现场验证。

<a id="T009"></a>
#### 表 9

**首次实质讨论**　[pp.11–12–13 S075](#S075)  
**原图表页**　p.12 · C026

![表 9](assets/table09.png)

<a id="C026"></a>
**Original caption:** Table 9 Visual-acquisition robustness and failure-mode analysis under inference-time perturbations.

**中文图表标题**　推理时扰动下视觉采集的稳健性与失效模式分析。

**阅读提示**　无图时准确率 0.541、宏平均 F1 0.140，误报率 0.0%，缺陷漏检率 100.0%。

<a id="S076"></a>
**Source**　p.13 · S076 · [图 11](#F011)

**Original:** We select one Undercut sample that was correctly predicted on the validation set and a nearby Normal sample. Their corresponding current–voltage waveforms, surface weld images, and the marked positions on the radiographic (RT) film are shown in Fig. 11. This example illustrates that, by visual inspection alone, it is extremely difficult to relate subtle differences in the waveforms and surface images to defect categories; in contrast, the MBGN model—through multimodal feature extraction, fusion, and detection—enables online defect identification.

**译文:** 作者选取一个验证集上正确预测的咬边样本及一个相邻的正常样本。图 11 给出对应的电流与电压波形、焊缝表面图像，以及在射线底片上的标记位置。该例说明仅凭肉眼，很难将波形和表面图中的细微差异与缺陷类别联系起来。作者据此展示 MBGN 通过多模态特征提取、融合和检测识别过程内缺陷的能力。

<a id="F011"></a>
#### 图 11

**首次实质讨论**　[p.13 S076](#S076)  
**原图表页**　p.12 · C011

![图 11](assets/fig11.png)

<a id="C011"></a>
**Original caption:** Fig. 11. Display and analysis of partial sample data.

**中文图表标题**　部分样本数据的展示与分析。

**阅读提示**　对照一个咬边位置与附近正常位置的成像、波形与射线底片标记。

<a id="S077"></a>
### 3.5 消融实验

**Source**　p.13 · S077

**Original:** 3.5. Ablation experiment

**译文:** 3.5 消融实验

<a id="S078"></a>
**Source**　p.13 · S078 · [图 12](#F012)

**Original:** To analyze the role of each module in the MBGN network, we conducted ablation experiments. Based on the dual-network architecture of MBGN, we trained three comparative models using the same dataset and training settings: 1) the feature extraction module (1DCNN) combined with a classification head; 2) the feature extraction module (ResNet-18) combined with a classification head; 3) MWFN (Multimodal Weighted-Fusion Network), in which multi-scale features are weighted within each modality and the final electrical and visual vectors are directly added before classification. A simplified schematic diagram of the ablation experiment models is shown in Fig. 12. In addition, a Concat-Fusion MLP was trained as a standard late-fusion baseline. It uses the same electrical and visual encoders as MBGN, but directly concatenates the high-level multimodal features before MLP classification, without BiFPN or Gate modules.

**译文:** 为分析 MBGN 各模块的作用，作者在同一数据集和训练设置下，基于双分支架构训练三个对比模型。（1）一维 CNN 特征提取模块配分类头。（2）ResNet-18 特征提取模块配分类头。（3）MWFN，在各模态内部对多尺度特征加权，分类前直接相加电信号与视觉向量。图 12 给出简化示意。此外训练标准后期融合基线 Concat-Fusion MLP，使用与 MBGN 相同的编码器，将高层多模态特征直接拼接后交给 MLP 分类，去掉 BiFPN 和 Gate。

<a id="F012"></a>
#### 图 12

**首次实质讨论**　[p.13 S078](#S078)  
**原图表页**　p.13 · C012

![图 12](assets/fig12.png)

<a id="C012"></a>
**Original caption:** Fig. 12. Schematic diagram of ablation experiment networks. a) 1DCNN-cls. b) ResNet-18-cls. c) MWFN. d) MBGN.

**中文图表标题**　消融实验网络示意。a）1DCNN-cls。b）ResNet-18-cls。c）MWFN。d）MBGN。

**阅读提示**　结合表 10 区分单模态、两种后期融合和完整 MBGN。Concat-Fusion MLP 的数值在表 10。

<a id="S079"></a>
**Source**　p.13 · S079 · [表 10](#T010)、[图 13](#F013)

**Original:** After training, the classification metrics of the five models are presented in Table 10. The Concat-Fusion MLP achieved an accuracy of 0.599 and a macro-F1 of 0.589, outperforming the single-modality baselines in macro-F1 but remaining lower than MBGN. This indicates that simple late fusion can use complementary multimodal information, but is less effective than bidirectional cross-scale fusion. In addition, removing the BiFPN module leads to a slightly higher accuracy, but its F1-score is lower than that of MBGN, indicating that weighted late fusion in MWFN is less effective for minority-class recognition. The confusion matrices of each model under their optimal classification metrics are shown in Fig. 13. It can be observed that after removing BiFPN, the detection capabilities for Hollow, L-crack, and Foreign-Object defects decrease, which is the main reason for the drop in F1-score.

**译文:** 表 10 列出训练后五个模型的指标。Concat-Fusion MLP 的准确率为 0.599、宏平均 F1 为 0.589，其宏平均 F1 高于单模态基线但低于 MBGN。简单后期融合能利用互补信息，但效果弱于双向跨尺度融合。去除 BiFPN 后准确率略高，F1 却低于 MBGN，说明 MWFN 的加权后期融合识别少数类的效果较弱。图 13 比较各模型在最优分类指标下的混淆矩阵。去除 BiFPN 后，空洞、纵向裂纹及异物的检测能力下降，是 F1 下滑的主要原因。

<a id="T010"></a>
#### 表 10

**首次实质讨论**　[p.13 S079](#S079)  
**原图表页**　p.14 · C027

![表 10](assets/table10.png)

<a id="C027"></a>
**Original caption:** Table 10 Comparison of classification performance of four models and Concat-Fusion MLP.

**中文图表标题**　四种结构及 Concat-Fusion MLP 的分类性能比较。

**阅读提示**　MWFN 准确率 0.750、宏平均 F1 0.599。MBGN 相应为 0.747 和 0.719。

<a id="F013"></a>
#### 图 13

**首次实质讨论**　[p.13 S079](#S079)  
**原图表页**　p.14 · C013

![图 13](assets/fig13.png)

<a id="C013"></a>
**Original caption:** Fig. 13. Confusion matrices of ablation models. a) 1DCNN-cls. b) ResNet-18-cls. c) MWFN. d) MBGN.

**中文图表标题**　消融模型的混淆矩阵。a）1DCNN-cls。b）ResNet-18-cls。c）MWFN。d）MBGN。

**阅读提示**　查看 MWFN 与 MBGN 的少数类变化，并结合原始计数判断证据强度。

<a id="S080"></a>
**Source**　p.13 · S080

**Original:** MWFN is used as a task-matched multimodal comparison model rather than a single-modality baseline. It directly tests whether simple weighted late fusion is sufficient for synchronized electrical-signal and molten-pool-image inputs. Compared with MWFN, the proposed MBGN introduces bidirectional cross-modal feature aggregation and gated recalibration, which provides a more structured interaction between arc-signal dynamics and weld-pool morphology. Although more general transformer-style multimodal fusion models could be explored, there is currently no widely accepted standard comparison architecture for this specific welding setting with synchronized 1-D electrical waveforms and 2-D molten-pool images.

**译文:** MWFN 是任务匹配的多模态比较模型。它直接测试对同步电信号和熔池图像进行简单加权后期融合是否足够。MBGN 采用跨模态双向特征聚合与门控重校准，使电弧信号动态和熔池形貌在更有结构的框架中交互。未来可探索更通用的 Transformer 类多模态融合模型。对同步一维电波形与二维熔池图像的焊接任务，目前尚无广泛接受的统一对照架构。

<a id="S081"></a>
### 3.6 相关性分析

**Source**　p.13 · S081

**Original:** 3.6. Correlation analysis

**译文:** 3.6 相关性分析

<a id="S082"></a>
**Source**　pp.13–14 · S082

**Original:** To verify that the 1-D-CNN module learns physically meaningful representations, we conduct correlation analyses between its intermediate-layer features and classical statistical descriptors of the current–voltage signals. For the four residual block groups in the 1-D-CNN, we aggregate channel-wise node activations in two ways—mean pooling and max pooling—yielding eight interpretable network features in total. As described in Section 2.5, we then compute correlations between each network feature and the time–frequency descriptors of current and voltage. The analyses are performed both overall (using all available samples) and separately within each defect category; due to limited sample size, the “Hollow” and “L-crack” categories are excluded. In our computation, if a time–frequency statistical feature of the current–voltage signal shows correlations below the threshold (0.5) with all eight network features, that time–frequency feature is excluded from subsequent analyses.

**译文:** 为验证一维 CNN 能否学习具有物理意义的表示，作者分析中间层特征与电流—电压信号传统统计描述量的相关性。对四组残差块，分别用均值池化和最大池化汇总按通道的节点激活，得到八种可解释的网络特征。按第 2.5 节，对各网络特征与电流、电压的时频描述量做相关分析，既分析总体样本，也按缺陷类别分析。由于样本有限，排除空洞和纵向裂纹。若某个时频统计特征与八种网络特征的相关性均低于 0.5，则从后续分析中排除。

<a id="S083"></a>
**Source**　p.14 · S083

**Original:** The 0.5 threshold is used only as an interpretability filter to keep the heatmaps readable; it is not a model decision threshold, and multiple weaker associations may still contribute jointly through nonlinear feature combinations.

**译文:** 阈值 0.5 用于筛选可解释性展示内容，以保持热图可读。模型不以此阈值作判决，多个较弱的关联仍可能通过非线性组合共同发挥作用。

<a id="S084"></a>
### 3.7 线性相关分析

**Source**　p.14 · S084

**Original:** 3.7. Linear correlation analysis

**译文:** 3.7 线性相关分析

<a id="S085"></a>
**Source**　pp.14–15 · S085 · [图 14](#F014)

**Original:** In the linear correlation analysis, Fig. 14 presents a compact top-12 Pearson heatmap between the mean- and max-pooled 1-D CNN stage features and handcrafted electrical-signal descriptors. To improve readability in the main manuscript, the descriptors were ranked according to the maximum absolute Pearson coefficient in the overall validation set, and only the top-12 descriptors are displayed; the complete Pearson heatmaps are provided in Supplementary Fig. S1. The selected descriptors are dominated by voltage waveform-shape statistics, such as skewness, kurtosis, interquartile range, and minimum, together with voltage short-time band-energy descriptors in the 200–1000 Hz, 1000–5000 Hz, and 5000–15000 Hz bands. Similar patterns are observed in the Overall, Normal, and Undercut panels, indicating that the learned electrical branch features are strongly associated with voltage spectral-energy distribution and waveform-shape information related to arc stability and metal-transfer fluctuation. The Foreign_object panel is retained only as a descriptive comparison and is interpreted cautiously because of its limited sample size.

**译文:** 图 14 给出均值和最大池化后的一维 CNN 各阶段表示与手工电信号描述量的前 12 项 Pearson 相关热图。作者按整个验证集中各描述量的最大绝对 Pearson 系数排序，仅在正文展示前 12 项。完整热图见补充图 S1。入选项以电压波形形态统计量为主，包括偏度、峰度、四分位距、最小值，以及 200–1000 Hz、1000–5000 Hz、5000–15000 Hz 频带的电压短时能量。总体、正常和咬边三组趋势相似，表明所学电信号特征与电压谱能量分布和波形形态高度关联，这些描述量与电弧稳定性及熔滴过渡波动有关。异物类别只作描述性比较，因样本少需谨慎解释。

<a id="F014"></a>
#### 图 14

**首次实质讨论**　[pp.14–15 S085](#S085)  
**原图表页**　p.15 · C014

![图 14](assets/fig14.png)

<a id="C014"></a>
**Original caption:** Fig. 14. Top-12 Pearson correlation heatmaps between pooled 1-D CNN stage features and handcrafted electrical-signal descriptors. The descriptors were selected according to their maximum absolute Pearson correlation in the overall validation set. a) Overall. b) Normal. c) Undercut. d) Foreign_object. The complete Pearson heatmaps are provided in Supplementary Fig. S1.

**中文图表标题**　池化后的一维 CNN 各阶段特征与手工电信号描述量的前 12 项 Pearson 相关热图。按整个验证集上的最大绝对 Pearson 相关系数选择描述量。a）总体。b）正常。c）咬边。d）异物。完整 Pearson 热图见补充图 S1。

**阅读提示**　读颜色符号和绝对大小，关注电压波形形态及多个频带的短时能量。

<a id="S086"></a>
### 3.8 非线性相关分析

**Source**　p.15 · S086

**Original:** 3.8. Nonlinear correlation analysis

**译文:** 3.8 非线性相关分析

<a id="S087"></a>
**Source**　p.15 · S087 · [图 15](#F015)

**Original:** In the nonlinear dependency analysis based on the Maximal Information Coefficient (MIC), in figure 15, the overall heatmap and the per-class results (“Normal” and “Undercut”) reveal a pattern broadly consistent with the linear findings but with stronger and more pervasive associations. Across stages S1–S4, MIC values are generally moderate to high (roughly 0.4–0.7 in many cells), with voltage-based descriptors dominating the top signals. In particular, short-time band energies of the voltage (e.g., 0–200 Hz ratio and mid–high bands around 1–5 kHz and 5–15 kHz) exhibit consistently elevated MIC with both mean- and max-pooled stage features, indicating that MBGN relies on time–frequency structure in the voltage to form its latent representations. Distribution-shape statistics of the voltage—kurtosis, skewness, interquartile range, minimum, range, and the absolute maximum—also show pronounced MIC, highlighting nonlinear coupling between burstiness/extreme events in the waveform and the network’s internal activations. Current-domain STBE features contribute as well, but the voltage channel is more salient overall (Fig. 15).

**译文:** 图 15 基于最大信息系数 MIC 分析非线性依赖。总体、正常和咬边的热图与线性结果大致一致，但关联更强、覆盖面更广。S1–S4 的 MIC 多为中高水平，不少格约 0.4–0.7，电压描述量居前。电压短时频带能量，如 0–200 Hz 能量占比，以及约 1–5 kHz 和 5–15 kHz 的中高频能量，与均值和最大池化后的各阶段特征均有持续较高的 MIC。作者据此认为潜在表示利用了电压的时频结构。电压的峰度、偏度、四分位距、最小值、极差和绝对最大值也有明显关联，显示突发或极端波形事件与网络激活存在非线性耦合。电流的短时频带能量特征也有贡献，总体上电压更突出。

<a id="F015"></a>
#### 图 15

**首次实质讨论**　[p.15 S087](#S087)  
**原图表页**　p.16 · C015

![图 15](assets/fig15.png)

<a id="C015"></a>
**Original caption:** Fig. 15. Nonlinear correlation calculation between convolution characteristics and statistical characteristics of one-dimensional data. a) Overall b) Normal c) Undercut.

**中文图表标题**　一维数据卷积特征与统计特征之间的非线性相关性。a）总体。b）正常。c）咬边。

**阅读提示**　MIC 反映依赖强度，解释时需和 Pearson 的正负方向区分。

<a id="S088"></a>
**Source**　pp.15–16 · S088

**Original:** Comparing classes, the “Normal” subset maintains the same MIC ordering as the overall set, suggesting the network consistently attends to voltage time–frequency patterns even without defect-driven distortions. The “Undercut” subset shows wider bands of elevated MIC and slightly higher values at deeper stages (notably S3/S4, often with max pooling), implying that MBGN further amplifies nonlinear cues tied to arc instabilities and edge thinning. As with the Pearson analysis, the “Foreign_object” class was excluded due to insufficient sample size. Taken together, the MIC results confirm that beyond linear trends, MBGN captures nonlinear dependencies linked to transient spectral content and higher-order distribution properties of the voltage signal—features that likely underpin its class-discriminative behavior.

**译文:** 分组比较时，正常子集的 MIC 排序与总体一致，表明即便没有缺陷引起的扰动，网络也持续关注电压时频模式。咬边子集中高 MIC 范围更广，深层特征尤其 S3、S4 的最大池化结果略高，作者认为 MBGN 可能放大了与电弧失稳和边缘减薄相关的非线性线索。异物类样本不足，未纳入非线性分析。综合而言，除线性趋势外，MBGN 捕获了与瞬态电压谱及高阶分布特征相联系的非线性依赖，作者认为这些特征可能支撑分类。

<a id="S089"></a>
**Source**　p.16 · S089

**Original:** Because the “Foreign_object” class contains too few samples, the nonlinear dependency estimates for this subset are statistically unstable and fail to pass our significance criterion. To avoid over-interpreting noisy effects driven by small-N bias, we therefore exclude Foreign_object from the nonlinear correlation analysis and only report classes with sufficient sample size.

**译文:** 异物样本数过少，非线性依赖估计不稳定，也未达到作者的显著性标准。为避免放大小样本偏差带来的噪声，非线性分析排除异物类，只报告样本量足够的类别。

<a id="S090"></a>
**Source**　p.16 · S090

**Original:** Physically, the voltage spectral-energy bands, extrema, skewness, and kurtosis highlighted by Pearson and MIC are consistent with arc stability, metal-transfer disturbance, and local heat-input fluctuation. The corresponding image attention patterns are also consistent with visible weld-edge thinning for Undercut, localized foreign-material appearance for Foreign_object, inner concavity for Hollow, and longitudinal crack-like morphology for L-crack. These observations support physical plausibility, but they should not be interpreted as causal proof of defect formation mechanisms.

**译文:** 从物理角度看，Pearson 与 MIC 突出的电压频带能量、极值、偏度和峰度，与电弧稳定性、熔滴过渡扰动和局部热输入波动相符。图像注意力模式也与咬边的焊缝边缘减薄、异物的局部异质外观、空洞的内部凹陷和纵向裂纹的纵向裂纹状形貌相符。这些观察支持物理合理性，缺陷形成的因果机制仍需另行验证。

<a id="S091"></a>
### 3.9 网络图像热图分析

**Source**　p.17 · S091

**Original:** 3.9. Heatmap analysis of the network on images

**译文:** 3.9 网络图像热图分析

<a id="S092"></a>
**Source**　p.17 · S092

**Original:** To further examine whether the visual branch of MBGN bases its decisions on physically meaningful image regions, Gradient- Weighted Class Activation Mapping (Grad-CAM) is employed as a post-hoc interpretability tool. Grad-CAM enables class-specific localization by identifying spatial regions in the input image that contribute most strongly to a given prediction.

**译文:** 为进一步检查视觉分支是否依据有物理意义的图像区域判别，作者采用梯度加权类激活映射（Grad-CAM）作事后解释。Grad-CAM 通过找出对特定预测贡献较大的输入图像区域，实现类别特异的定位。

<a id="S093"></a>
**Source**　p.17 · S093

**Original:** Specifically, Grad-CAM is applied to the last convolutional block of the ResNet-18 image backbone, which provides high-level semantic representations while retaining sufficient spatial structure for localization. For each validation sample, a forward pass of the multimodal network is first performed using the paired electrical signal sequence and weld-pool image. The predicted class score is then selected, and its gradient with respect to the feature maps of the target convolutional layer is computed via back-propagation.

**译文:** 将 Grad-CAM 应用于 ResNet-18 视觉主干网络的最后一个卷积块。该层兼具高层语义表示和足够的空间结构，适于定位。对每个验证样本，先用配对电信号序列与熔池图像进行多模态网络前向传播，再选取预测类别的分数，通过反向传播计算该分数关于目标卷积层特征图的梯度。

<a id="S094"></a>
**Source**　p.17 · S094

**Original:**

```text
Let Ak denote the k-th channel of the selected feature map, and yc represent the logit corresponding to the predicted class c. The
importance weight αck for each channel is obtained by globally averaging the gradients over the spatial dimensions:
1 ∑∑ ∂yc
         αck =
                 Z i j ∂Akij
```

**译文:** 设 $A^k$ 表示选定特征图的第 $k$ 个通道，$y^c$ 为预测类别 $c$ 的 logit。对空间位置上的梯度取全局平均，得到通道重要性权重。

$$\alpha_k^c=\frac1Z\sum_i\sum_j\frac{\partial y^c}{\partial A_{ij}^k}.$$

<a id="S095"></a>
**Source**　pp.17–18 · S095

**Original:**

```text
where Z denotes the number of spatial locations. The class-specific Grad-CAM map is then computed as a weighted linear com­
bination of the activation maps followed by a rectified linear unit (ReLU):
(              )
                               ∑
         LcGrad− cam = ReLU         αck Ak
                                k
```

**译文:** $Z$ 是空间位置数。将激活图做加权线性组合后取 ReLU，得到类别特异的 Grad-CAM 图。

$$L_{\mathrm{Grad-CAM}}^c=\mathrm{ReLU}\left(\sum_k \alpha_k^c A^k\right).$$

<a id="S096"></a>
**Source**　p.18 · S096

**Original:** The resulting activation map is up-sampled to the original image resolution using bilinear interpolation, normalized to the range [1], and overlaid on the corresponding weld-pool image for visualization.

**译文:** 通过双线性插值将激活图上采样至原图分辨率，将其归一化后叠加在对应熔池图像上。原文归一化区间写作 [1]，见核对说明。

<a id="S097"></a>
**Source**　p.18 · S097

**Original:** Although MBGN performs joint decision-making based on both electrical signals and visual information, Grad-CAM analysis is applied exclusively to the image branch to reveal the spatial evidence that supports the final classification under the given multimodal input. This allows direct inspection of whether the visual stream attends to regions consistent with welding physics and known defect characteristics. Therefore, these maps are qualitative checks of the visual branch under paired multimodal input, not a complete explanation of the fused decision process.

**译文:** MBGN 同时使用电信号和视觉信息作联合决策。这里的 Grad-CAM 只用于图像分支，显示在配对多模态输入条件下支持最终分类的空间证据。这样可直观检查视觉分支是否关注与焊接物理及已知缺陷特征相符的位置。这些图提供视觉分支的定性检查，融合决策的完整解释仍需其他证据。

<a id="S098"></a>
**Source**　p.18 · S098

**Original:** The resulting visualizations consistently highlight defect contours, weld-edge irregularities, and non-uniform molten pool regions, indicating that the model learns discriminative and physically relevant visual features rather than relying on spurious background cues. Furthermore, distinct attention patterns are observed across different defect categories: This interpretation is physically plausible but remains qualitative; therefore, a perturbation-based visual occlusion analysis was further conducted to provide a quantitative check.

**译文:** 可视化反复突出缺陷轮廓、焊边不规则及不均匀的熔池区域。作者认为模型学习了兼具辨别力和物理相关性的视觉特征，并观察到不同类别的注意力模式。这一解释具有物理合理性，仍属定性判断，因此作者追加了基于扰动的视觉遮挡分析做定量核对。

<a id="S099"></a>
**Source**　p.18 · S099

**Original:** • Normal – the model attends primarily to the arc region and the lower-right boundary of the seam. • Undercut – attention concentrates on the left side of the weld pool. • Foreign_object – the central seam area dominates the activation. • Hollow – the lower-left portion of the seam is highlighted. • L-crack – the right side of the weld pool attracts the strongest response.

**译文:**

- 正常：主要关注电弧区域和焊缝右下边界。
- 咬边：激活集中在熔池左侧。
- 异物：焊缝中部激活最明显。
- 空洞：焊缝左下部分被突出显示。
- 纵向裂纹：熔池右侧响应最强。

<a id="S100"></a>
**Source**　p.18 · S100 · [图 16](#F016)

**Original:** Fig. 16 presents representative images together with their corresponding Grad-CAM heat-maps for each defect class.

**译文:** 图 16 展示各类缺陷的代表性熔池图像及对应 Grad-CAM 热图。

<a id="F016"></a>
#### 图 16

**首次实质讨论**　[p.18 S100](#S100)  
**原图表页**　p.17 · C016

![图 16](assets/fig16.png)

<a id="C016"></a>
**Original caption:** Fig. 16. Comparison of weld-pool images and corresponding heatmaps across different defect categories.

**中文图表标题**　不同缺陷类别的熔池图像及相应热图对比。

**阅读提示**　代表性样本的 Grad-CAM 可显示图像区域贡献，需结合遮挡实验和样本数量解读。

<a id="S101"></a>
### 3.10 定量视觉遮挡分析

**Source**　p.18 · S101

**Original:** 3.10. Quantitative visual occlusion analysis

**译文:** 3.10 定量视觉遮挡分析

<a id="S102"></a>
**Source**　p.18 · S102 · [表 11](#T011)

**Original:** To complement the qualitative Grad-CAM visualization, a perturbation-based visual occlusion-sensitivity analysis was performed on the molten-pool images. Each validation image was divided into a 7 x 7 grid, and one grid cell was masked at a time while keeping the paired electrical signals unchanged. For each masked region, we measured the change in true-class probability, prediction margin, final predicted label, and classification metrics. This analysis provides a quantitative check of whether the image branch relies on physically relevant weld-pool regions rather than arbitrary background cues (Table 11).

**译文:** 为补充 Grad-CAM 的定性可视化，作者对熔池图像做基于扰动的遮挡敏感性分析。每张验证图像划成 7 × 7 网格，每次遮挡一个单元，保持配对的电信号不变。对每个遮挡位置，测量真实类别概率、预测边际、最终标签和分类指标的变化，定量核查视觉分支是否使用与焊接物理相关的熔池区域（表 11）。

<a id="T011"></a>
#### 表 11

**首次实质讨论**　[p.18 S102](#S102)  
**原图表页**　p.18 · C028

![表 11](assets/table11.png)

<a id="C028"></a>
**Original caption:** Table 11 Quantitative visual occlusion-sensitivity analysis of MBGN.

**中文图表标题**　MBGN 的定量视觉遮挡敏感性分析。

**阅读提示**　中央单元遮挡使宏平均 F1 降至 0.443，下部中央遮挡使真实类概率平均下降 0.0465。

<a id="S103"></a>
**Source**　p.18 · S103 · [图 17](#F017)

**Original:** The clean input achieved an accuracy of 0.755 and a macro-F1 of 0.755. Masking the central grid cell (row 3, column 3) changed 47 predictions and reduced macro-F1 to 0.443, with a mean true-class probability drop of 0.0257 and a mean prediction-margin drop of 0.0516. The most sensitive region was located at row 5, column 3, corresponding to the lower-central image area (y = 160–192, x = 96–128 in the resized 224 x 224 image). Occluding this region changed 67 predictions, reduced accuracy to 0.704 and macro-F1 to 0.468, and produced the largest mean true-class probability drop (0.0465) and margin drop (0.0925). The 7 x 7 heatmap further shows that high-sensitivity cells are concentrated mainly in the lower-central weld-pool and bead-formation region. These results support the Grad-CAM observations and indicate that MBGN uses spatial evidence related to molten-pool morphology and weld-edge formation, while still remaining a post-hoc association rather than causal proof of defect generation (Fig. 17).

**译文:** 干净输入的准确率及宏平均 F1 均为 0.755。遮挡中央网格（第 3 行、第 3 列）改变 47 个预测，宏平均 F1 降至 0.443，真实类别概率均值下降 0.0257，预测边际均值下降 0.0516。最敏感区域为第 5 行、第 3 列，对应 224 × 224 图像的下部中央（纵坐标 160–192，横坐标 96–128）。遮挡后有 67 个预测改变，准确率降到 0.704，宏平均 F1 为 0.468，产生最大的真实类别概率均值降幅（0.0465）和预测边际均值降幅（0.0925）。7 × 7 热图显示，高敏感单元主要在熔池下方中央与焊道形成区。结果支持 Grad-CAM 的观察，表明 MBGN 使用与熔池形貌和焊边形成相关的空间证据。这仍属于事后关联，缺陷生成的因果机制需要独立证据（图 17）。

<a id="F017"></a>
#### 图 17

**首次实质讨论**　[p.18 S103](#S103)  
**原图表页**　p.19 · C017

![图 17](assets/fig17.png)

<a id="C017"></a>
**Original caption:** Fig. 17. Mean true-class probability drop under 7 x 7 visual occlusion.

**中文图表标题**　7 × 7 视觉遮挡下真实类别概率的平均降幅。

**阅读提示**　高敏感单元主要在下部中央。表 11 同时报告宏平均 F1，二者对应的最敏感格可以不同。

<a id="S104"></a>
**Source**　p.18 · S104

**Original:** Across the evaluated metrics, MBGN performs better than the single-modality baselines, particularly in macro-F1. Its combination of electrical and visual cues, bidirectional feature fusion, and cross-attention gating improves minority-class discrimination while maintaining competitive overall accuracy. The correlation analysis links learned electrical-signal features to established signal-processing descriptors, providing supporting evidence for the physical plausibility of the learned representations.

**译文:** 从所评估的指标看，MBGN 优于单模态基线，宏平均 F1 尤其明显。结合电信号和视觉、双向特征融合及交叉注意力门控，提高了少数类别的区分能力，并保持有竞争力的总体准确率。相关性分析把学到的电信号特征与常用信号处理描述量关联起来，为学习表示的物理合理性提供支持。

<a id="S105"></a>
**Source**　p.18 · S105

**Original:** The visual occlusion analysis further supports the Grad-CAM interpretation by showing that performance is most sensitive to masking the lower-central weld-pool and bead-formation region. These findings support the potential of MBGN for in-process weld-defect monitoring under the investigated production conditions, while broader deployment requires further validation.

**译文:** 视觉遮挡分析进一步支持 Grad-CAM 的解释。遮挡熔池下部中央及焊道形成区时，模型性能对遮挡最为敏感。这些结果支持 MBGN 在所考察生产条件下用于过程内焊接缺陷监测的潜力。更广泛的部署还需继续验证。

<a id="S106"></a>
## 4. 结论

**Source**　p.18 · S106

**Original:** 4. Conclusion

**译文:** 4. 结论

<a id="S107"></a>
**Source**　p.18 · S107

**Original:** This work presents the following contributions:

**译文:** 本文的贡献包括以下三项。

<a id="S108"></a>
**Source**　p.18 · S108

**Original:** 1. Field-based data acquisition – We collected synchronized multimodal data (current–voltage waveforms and weld-pool images) on an industrial GMAW line in collaboration with a production facility, providing a realistic benchmark for in-process defect detection.

**译文:**

1. 现场数据采集。与生产企业合作采集工业 GMAW 产线的同步多模态数据（电流—电压波形及熔池图像），为过程内缺陷检测提供现实基准。

<a id="S109"></a>
**Source**　p.19 · S109

**Original:** 2. MBGN architecture – We designed a Multi-modal BiFPN Gate Network (MBGN) that jointly processes electrical and visual streams through residual-dilated 1-D CNNs, a ResNet-18 visual encoder, a bidirectional feature-pyramid, and a cross-attention gate. MBGN outperforms single-modality baselines (ResNet50-Cls, MSTCN-Cls) on both accuracy (0.747) and macro-F1 (0.719). 3. Interpretability and validation − Grad-CAM and quantitative visual occlusion analysis suggest that the image branch attends to semantically relevant weld-pool regions, while correlation analysis between learned 1-D CNN features and conventional statistical descriptors indicates that the network captures physically meaningful signal characteristics.

**译文:**

2. MBGN 架构。设计多模态 BiFPN 门控网络 MBGN，用残差扩张一维 CNN、ResNet-18 视觉编码器、双向特征金字塔及交叉注意力门控共同处理电信号与视觉数据流。相较单模态基线（ResNet50-Cls、MSTCN-Cls），MBGN 的准确率（本节列 0.747）与宏平均 F1（0.719）均更高。
3. 可解释性与验证。Grad-CAM 和定量视觉遮挡分析提示，图像分支关注对判断有意义的熔池区域。对一维 CNN 学习特征与常用统计描述量进行的相关性分析，表明网络捕获了有物理意义的信号特征。

<a id="S110"></a>
## 5. 局限与未来工作

**Source**　p.19 · S110

**Original:** 5. Limitations and future work

**译文:** 5. 局限与未来工作

<a id="S111"></a>
**Source**　p.19 · S111

**Original:** The dataset, although collected under production conditions, contains a limited number of rare defects, which restricts robust evaluation of minority classes. Future work will expand the rare-defect inventory through deeper collaboration with the manufacturing partner, investigate lighter backbones for edge inference, and evaluate whether additional sensing modalities such as acoustic or infrared signals can further reduce false positives and improve sensitivity to subtle defects. A complete sensor-to-decision latency analysis, including acquisition, synchronization, cropping, interpolation, and I/O, should also be validated on the production line.

**译文:** 数据来自生产现场，稀有缺陷数量有限，约束了少数类的稳健评估。未来将通过加深与制造企业合作扩充稀有缺陷数据，研究更轻量的边缘端主干网络，并评估声学或红外等新增模态能否减少误报、提高细微缺陷识别灵敏度。还应在生产线上验证完整的传感到决策延迟，包括采集、同步、裁剪、插值和 I/O。

<a id="S112"></a>
**Source**　p.19 · S112

**Original:** The current validation is restricted to Q345R fillet welds with several plate-thickness/process-parameter groups; direct transfer to other materials, joint forms, welding procedures, or fully online preprocessing pipelines remains to be demonstrated. In addition, Hollow and L-crack samples are concentrated in individual seams, so strict seam-level hold-out or leave-one-seam-out validation is not statistically appropriate for the present five-class setting because it would either remove these classes from training or make them absent from testing. Future work will prioritize the collection of rare-defect samples across multiple seams and parameter groups through continued collaboration with the manufacturing partner, enabling rigorous group-level validation.

**译文:** 当前验证仅涵盖 Q345R 角焊缝和若干板厚、工艺参数组合。能否直接推广到其他材料、接头形式、焊接工艺及全在线预处理流程仍待验证。空洞和纵向裂纹分别集中在个别焊缝，严格按焊缝留出或逐条焊缝留一，可能让这两个类别从训练集或测试集消失，故不适于当前五分类数据。未来优先与制造方合作，在多条焊缝和多个参数组中采集稀有缺陷，以支持严格按组验证。

<a id="S113"></a>
**Source**　p.19 · S113

**Original:** Future work with larger and more balanced datasets will also include broader transformer-style or attention-based multimodal comparison models, once their adaptation to synchronized welding signals and molten-pool imagery can be evaluated under a fair protocol.

**译文:** 未来将用更大、更均衡的数据集，在公平的评价方案下，验证更广泛的 Transformer 或基于注意力的多模态模型能否适配同步焊接信号与熔池图像，并将它们纳入对比。

<a id="S114"></a>
### CRediT 作者贡献声明

**Source**　p.19 · S114

**Original:** CRediT authorship contribution statement

**译文:** CRediT 作者贡献声明

<a id="S115"></a>
**Source**　p.19 · S115

**Original:** Xuefeng Zhao: Writing – original draft, Validation, Methodology, Formal analysis, Conceptualization. Yang She: Software. Giulio Mattera: Writing – review & editing. Lichao Hu: Data curation. Zhen Sun: Investigation. Yan Li: Software. Xinghua Yu: Writing – review & editing, Supervision, Project administration.

**译文:** Xuefeng Zhao：初稿撰写、验证、方法学、正式分析、概念构思。Yang She：软件。Giulio Mattera：审阅与编辑。Lichao Hu：数据整理。Zhen Sun：调查研究。Yan Li：软件。Xinghua Yu：审阅与编辑、监督指导、项目管理。

<a id="S116"></a>
### 经费

**Source**　p.19 · S116

**Original:** Funding

**译文:** 经费

<a id="S117"></a>
**Source**　p.19 · S117

**Original:** No funds, grants, or other support was received for this study.

**译文:** 本研究未获得经费、科研资助或其他支持。

<a id="S118"></a>
### 利益冲突声明

**Source**　p.19 · S118

**Original:** Declaration of competing interest

**译文:** 利益冲突声明

<a id="S119"></a>
**Source**　pp.19–20 · S119

**Original:** The authors declare the following financial interests/personal relationships which may be considered as potential competing interests: Author Lichao Hu is affiliated with Chongqing Midea General Refrigeration Equipment Co., Ltd. The data used in this study were collected on an industrial production line in collaboration with Midea Group, and portions of the dataset are subject to proprietary and commercial confidentiality restrictions. The remaining authors declare that they have no additional financial or non-financial interests relevant to the content of this article.

**译文:** 作者披露下列可能被视为潜在利益冲突的经济利益或个人关系。Lichao Hu 隶属重庆美的通用制冷设备有限公司。研究数据采集自与美的集团合作的工业生产线，部分数据受到专有信息及商业保密限制。其余作者声明不存在与本文内容相关的其他经济或非经济利益。

<a id="S120"></a>
### 数据可用性

**Source**　p.20 · S120

**Original:** Data availability

**译文:** 数据可用性

<a id="S121"></a>
**Source**　p.20 · S121

**Original:** The multimodal dataset (current–voltage waveforms and molten-pool imagery) generated and analyzed during the current study was collected on an industrial production line in collaboration with Midea Group. Due to proprietary and commercial confidentiality agreements with the industrial partner, the raw data are not publicly available. However, the processed data and relevant experimental results may be available from the corresponding author (xyu@bit.edu.cn) upon reasonable request for non-commercial academic research purposes.

**译文:** 研究所生成并分析的多模态数据（电流—电压波形及熔池图像）采集自与美的集团合作的工业生产线。因与合作方签有专有信息及商业保密协议，原始数据未公开。面向非商业学术研究，如提出合理请求，通讯作者（xyu@bit.edu.cn）可能提供处理后数据和相关实验结果。

<a id="S122"></a>
### 参考文献

**Source**　p.20 · S122

**Original:** References

**译文:** 参考文献

<a id="R001"></a>
**Source**　p.20 · R001

**Original:** [1] S. Zhao, et al., A lumped-parameter model for sound generation in gas metal arc welding, Mech. Syst. Sig. Process. 147 (2021) 107085.

**译文（题名）**　气体保护金属电弧焊声产生的集中参数模型

<a id="R002"></a>
**Source**　p.20 · R002

**Original:** [2] I.G. Pérez, V. Meruane, P.F. Mendez, Deep-learning based analysis of metal-transfer images in GMAW process, J. Manuf. Process. 85 (2023) 9–20.

**译文（题名）**　基于深度学习的 GMAW 熔滴过渡图像分析

<a id="R003"></a>
**Source**　p.20 · R003

**Original:** [3] X. Zhao, et al., SWRD: a dataset of radiographic image of seam weld for defect detection, J. Nondestr. Eval. 44 (2) (2025) 1–15.

**译文（题名）**　SWRD：用于缺陷检测的连续焊缝射线图像数据集

<a id="R004"></a>
**Source**　p.20 · R004

**Original:** [4] F. Zuo, J. Liu, M. Fu, Z. Wen, An end-to-end intelligent welding defect detection system for low-quality X-ray images with adaptive progressive learning, Expert Syst. Appl. 279 (2025) 127428.

**译文（题名）**　基于自适应渐进学习的低质量 X 射线图像端到端智能焊接缺陷检测系统

<a id="R005"></a>
**Source**　p.20 · R005

**Original:** [5] F. Zuo, et al., An X-ray-based automatic welding defect detection method for special equipment system, IEEE/ASME Trans. Mechatron. 29 (3) (2023) 2241–2252.

**译文（题名）**　面向特种设备系统的 X 射线自动焊接缺陷检测方法

<a id="R006"></a>
**Source**　p.20 · R006

**Original:** [6] R.H. Murta, F.d.A. Vieira, V.O. Santos, E.P. de Moura, Welding defect classification from simulated ultrasonic signals, J. Nondestr. Eval. 37 (3) (2018) 40.

**译文（题名）**　利用模拟超声信号对焊接缺陷进行分类

<a id="R007"></a>
**Source**　p.20 · R007

**Original:** [7] X. Wang, et al., A comprehensive review of welding defect recognition from X-ray images, J. Manuf. Process. 140 (2025) 161–180.

**译文（题名）**　基于 X 射线图像的焊接缺陷识别综述

<a id="R008"></a>
**Source**　p.20 · R008

**Original:** [8] Y. Sun, P. Bai, H.-Y. Sun, P. Zhou, Real-time automatic detection of weld defects in steel pipe, Ndt & E Int. 38 (7) (2005) 522–528.

**译文（题名）**　钢管焊接缺陷的实时自动检测

<a id="R009"></a>
**Source**　p.20 · R009

**Original:** [9] Z. Zhang, et al., Multisensor-based real-time quality monitoring by means of feature extraction, selection and modeling for Al alloy in arc welding, Mech. Syst. Sig. Process. 60 (2015) 151–165.

**译文（题名）**　利用特征提取、选择和建模实现铝合金电弧焊的多传感器实时质量监测

<a id="R010"></a>
**Source**　p.20 · R010

**Original:** [10] M. Rohe, et al., Detecting process anomalies in the GMAW process by acoustic sensing with a convolutional neural network (CNN) for classification, J. Manuf. Mater. Process. 5 (4) (2021) 135.

**译文（题名）**　用声学传感和卷积神经网络分类检测 GMAW 过程异常

<a id="R011"></a>
**Source**　p.20 · R011

**Original:** [11] M.F.M. Yusof, et al., Identification of weld defect through the application of denoising method to the sound signal acquired during pulse mode laser welding, Weld. World 67 (5) (2023) 1267–1281, https://doi.org/10.1007/s40194-023-01472-z.

**译文（题名）**　用脉冲激光焊声音去噪识别焊接缺陷

<a id="R012"></a>
**Source**　p.20 · R012

**Original:** [12] R. Yu, T. Zhang, Y. Huang, K. Wang, Monitoring of gas metal arc welding process using optical temperature measurement and neural network modelling, Measurement (2025) 116934.

**译文（题名）**　利用光学测温与神经网络建模监测 GMAW

<a id="R013"></a>
**Source**　p.20 · R013

**Original:** [13] M. Luttmer, et al., Towards data-driven quality monitoring for advanced metal inert gas welding processes in body-in-white, J. Manuf. Syst. 77 (2024) 875–891.

**译文（题名）**　面向白车身先进熔化极惰性气体保护焊的数据驱动质量监测

<a id="R014"></a>
**Source**　p.20 · R014

**Original:** [14] G. He, X. Gao, H. Yang, AETMC-FCVT: an end-to-end welding defect detection and classification method based on magneto-optical infrared bi-imaging system, Mech. Syst. Sig. Process. 224 (2025) 112058.

**译文（题名）**　AETMC-FCVT：基于磁光—红外双成像系统的端到端焊接缺陷检测方法

<a id="R015"></a>
**Source**　p.20 · R015

**Original:** [15] B. Wang, S.J. Hu, L. Sun, T. Freiheit, Intelligent welding system technologies: State-of-the-art review and perspectives, J. Manuf. Syst. 56 (2020) 373–391.

**译文（题名）**　智能焊接系统技术的研究现状与展望

<a id="R016"></a>
**Source**　p.20 · R016

**Original:** [16] B. Zhang, et al., Enhancing weld inspection through comparative analysis of traditional algorithms and deep learning approaches, J. Nondestr. Eval. 43 (2) (2024) 38.

**译文（题名）**　通过传统算法与深度学习方法对比改进焊缝检验

<a id="R017"></a>
**Source**　p.20 · R017

**Original:** [17] X. Wang, et al., On the effect of the attention mechanism for automatic welding defects detection based on deep learning, Expert Syst. Appl. 268 (2025) 126386.

**译文（题名）**　注意力机制对自动焊接缺陷检测的影响

<a id="R018"></a>
**Source**　p.20 · R018

**Original:** [18] S. Wang, et al., 3DWDC-net: an improved 3DCNN with separable structure and global attention for weld internal defect classification based on phased array ultrasonic tomography images, Mech. Syst. Sig. Process. 229 (2025) 112564.

**译文（题名）**　基于相控阵超声层析图像、采用可分离结构和全局注意力的焊缝内部缺陷分类网络 3DWDC-net

<a id="R019"></a>
**Source**　p.20 · R019

**Original:** [19] Muñoz Chávez, J.J., M.N. de Souza Lira, J. da Cruz Payão Filho, and S.C.A. Alfaro, Multimodal monitoring and predictive modeling for stability and overlap control in arc-based directed energy deposition. Welding in the World, 2026 10.1007/s40194-025-02309-7.

**译文（题名）**　面向电弧定向能量沉积稳定性与搭接量控制的多模态监测和预测建模

<a id="R020"></a>
**Source**　p.20 · R020

**Original:** [20] R. Kumar, S. Chattopadhyaya, S. Kumar, Influence of welding current on bead shape, mechanical and structural property of tungsten inert gas welded stainless steel plate, Mater. Today Proc. 2 (4–5) (2015) 3342–3349.

**译文（题名）**　钨极惰性气体保护焊低碳钢中焊接电流对焊道形状、力学性能和组织特性的影响

<a id="R021"></a>
**Source**　p.20 · R021

**Original:** [21] D.-Y. Kim, H.W. Lee, J. Yu, J.-K. Park, Application of convolutional neural networks for classifying penetration conditions in GMAW processes using STFT of welding data, Appl. Sci. 14 (11) (2024) 4883.

**译文（题名）**　利用焊接数据短时傅里叶变换与卷积神经网络对 GMAW 熔透状态分类

<a id="R022"></a>
**Source**　p.20 · R022

**Original:** [22] K. Nomura, K. Fukushima, T. Matsumura, S. Asai, Burn-through prediction and weld depth estimation by deep learning model monitoring the molten pool in gas metal arc welding with gap fluctuation, J. Manuf. Process. 61 (2021) 590–600.

**译文（题名）**　坡口间隙波动下，基于深度学习监测 GMAW 熔池以预测烧穿与估计熔深

<a id="R023"></a>
**Source**　p.20 · R023

**Original:** [23] H. Li, et al., Defects detection of GMAW process based on convolutional neural network algorithm, Sci. Rep. 13 (1) (2023) 21219.

**译文（题名）**　基于卷积神经网络的 GMAW 过程缺陷检测

<a id="R024"></a>
**Source**　p.20 · R024

**Original:** [24] C. Shi, et al., Welding defect monitoring based on multi-scale feature fusion of molten pool videos, Sensors 24 (20) (2024) 6561.

**译文（题名）**　基于熔池视频多尺度特征融合的焊接缺陷监测

<a id="R025"></a>
**Source**　p.20 · R025

**Original:** [25] M. Mobaraki, et al., Multi-modal data improves real-time defect classification deep learning models for fillet joints in gas metal arc welding, Int. J. Adv. Manuf. Technol. (2025) 1–9.

**译文（题名）**　多模态数据改善 GMAW 角接接头的实时缺陷分类深度学习模型

<a id="R026"></a>
**Source**　p.20 · R026

**Original:** [26] X. Zeng, et al., Defect identification for mild steel in arc welding using multi-sensor and neighborhood rough set approach, Appl. Sci. 14 (12) (2024) 4978.

**译文（题名）**　基于多传感器和邻域粗糙集的低碳钢电弧焊缺陷识别

<a id="R027"></a>
**Source**　p.20 · R027

**Original:** [27] K. Liu, et al., DSFusion: Infrared and visible image fusion method combining detail and scene information, Pattern Recogn. 154 (2024) 110633.

**译文（题名）**　DSFusion：结合细节和场景信息的红外与可见光图像融合

<a id="R028"></a>
**Source**　p.20 · R028

**Original:** [28] M. Li, et al., DCFusion: Difference correlation-driven fusion mechanism of infrared and visible images, Pattern Recogn. 158 (2025) 111002.

**译文（题名）**　DCFusion：结合差异与相关机制的红外与可见光图像融合

<a id="R029"></a>
**Source**　p.20 · R029

**Original:** [29] X. Zhou, et al., CMACF: Transformer-based cross-modal attention cross-fusion model for systemic lupus erythematosus diagnosis combining Raman spectroscopy, FTIR spectroscopy, and metabolomics, Inf. Process. Manag. 61 (6) (2024) 103804.

**译文（题名）**　CMACF：基于 Transformer 的跨模态注意力交叉融合，用于联合拉曼与傅里叶变换红外光谱诊断系统性红斑狼疮

<a id="R030"></a>
**Source**　p.20 · R030

**Original:** [30] X. Zhou, et al., Cross branch co-attention network multimodal models based on raman and FTIR spectroscopy for diagnosis of multiple selected cancers, Appl. Soft Comput. 166 (2024) 112204.

**译文（题名）**　基于拉曼与傅里叶变换红外光谱的跨分支协同注意网络多种特定癌症诊断

## 术语对照

| 英文 | 中文 | 本文用法 |
| --- | --- | --- |
| Gas Metal Arc Welding (GMAW) | 熔化极气体保护焊 | Q345R 角焊缝，保护气含 Ar 和 CO₂ |
| RT / radiographic testing | 射线检测 | 焊后定位缺陷以赋予监督标签 |
| Molten pool / weld pool | 熔池 | 相机过程内采集的目标区域 |
| Undercut | 咬边 | 表 2 中最多的缺陷类 |
| Foreign Object | 异物 | 监督分类标签 |
| Hollow | 空洞 | 沿用原文标签，具体机制需核查 |
| L-crack | 纵向裂纹 | 监督分类标签，样本有限 |
| BiFPN | 双向特征金字塔网络 | 多尺度跨模态双向聚合 |
| Weighted late fusion | 加权后期融合 | MWFN 的对照方案 |
| Macro-F1 | 宏平均 F1 | 各类别 F1 的等权平均 |
| STBE | 短时频带能量 | 电信号的时频描述量 |
| MIC | 最大信息系数 | 评估潜在特征与手工描述量的依赖 |
| Grad-CAM | 梯度加权类激活映射 | 视觉分支的事后可解释性分析 |

<a id="reading-notes"></a>
## 精读整理

### 这篇文章解决了什么

作者在美的的 GMAW 产线上，对 16 条 Q345R 钢角焊缝同步采集电流、电压和熔池图像，并把焊后 X 射线检测结果回填为过程样本标签。以熔池图像时间戳为锚，每张图像配对一个前后各 50 ms 的电信号窗口。模型对配对样本做五分类，判别正常、咬边、异物、空洞和纵向裂纹。数据流可沿图 1、图 3–5 和图 7 阅读。

投入主要工作的是两件事。第一，建立 **过程传感记录 → 焊缝位置 → 焊后缺陷标签** 的监督链，让现场信号有可追溯的质量参照。第二，让电信号中的时间变化与图像中的形貌变化在分类前发生交互。BiFPN 汇集两个层级的跨模态特征，Gate 用电信号查询视觉信息，再对特征做门控重校准。模型具备焊接场景针对性，其电压特征相关分析和视觉遮挡分析发生在训练后。

### 实验结果的正确口径

| 证据 | 原文数据 | 读法 |
| --- | ---: | --- |
| 主比较，表 5 | MBGN 准确率 0.748、宏平均 F1 0.719 | 对 436 个留出配对样本的五类识别结果 |
| 结构比较，表 10 | MWFN 0.750 / 0.599，MBGN 0.747 / 0.719 | 宏平均 F1 提高 0.120，准确率相近；这是完整融合方案对比 |
| 稀有类，图 9 与表 6 | 空洞 1/2，纵向裂纹 1/2 | 已观察到正确识别，当前样本量不足以估计稳定检出能力 |
| 统计不确定性，表 7 | 宏平均 F1 0.714，95% CI 0.466–0.856 | 论文报告的 bootstrap 区间较宽；严格按焊缝独立验证仍待开展 |
| 视觉退化，表 9 | 缺图宏平均 F1 0.140，缺陷漏检率 100% | 属于对既有检查点的推理时压力测试。重新训练的电信号单模态基线是另一组实验 |
| 推理计时，表 4 | 4.28 ms/样本 | 仅模型前向。相机采集为 8 Hz，中心窗口需要等待帧后约 50 ms，整链路仍待实测 |

图 9(c) 还显示，**59 个正常样本被判成咬边，47 个咬边样本被判成正常**。这是你选咬边作为首个研究对象时可直接使用的基线证据。16 条焊缝和 93,570 组配对样本并不等同于同数量的独立缺陷事件。图 6 展示下采样后的 2,166 组，表 2 才是全量配准数据的分布。正文没有说明这些咬边窗口对应多少个独立事件。

### 对你的 GMAW 选题有什么启发

| MBGN 已做到 | 你的题目可以验证的问题 | 对照设计 |
| --- | --- | --- |
| 以帧时间戳同步图像和电信号，再按焊段相对位置赋予 RT 标签（第 3–4 页，图 5） | 机器人弧长位置、RT 标记点和时间戳联合配准，能否减小焊缝位置标签的偏差？ | 固定模型，比较焊段相对位置映射与实际轨迹映射。在工件上设置可共同识别的参考点，报告纵向定位误差，并测试时间偏移对结果的影响 |
| 以中心 100 ms 窗口做配对样本分类（第 3–4、9 页） | 同一位置之前的热输入和熔池演化历史，能否提高连续咬边区段的识别与定位？ | 同一编码器和划分下，对比原居中窗口、等长历史窗口与多尺度历史窗口。增加可用的物理观测量或经验证的热历史代理量，单独消融。仅在有测温或校准热模型时把代理量解释为温度历史 |
| 以帧级宏平均 F1 评价留出样本（第 7、10–11、19 页） | 模型能否在一条没参与训练的焊缝上检出完整事件，并给出可核验的起止位置？ | 将咬边按连续缺陷区段标注为事件，按焊缝分组，报告事件级召回率、误报数/米及起止位置误差，同时保留帧级指标供对比 |

**建议先验证一个命题**　对于未见焊缝，使用可校准的时空配准和过去的过程历史，能否同时改善咬边事件召回率与纵向定位？从咬边入手的理由是它在这篇论文中有 936 个配对样本，适合先核实这些样本来自多少条焊缝、多少个独立区段，再决定组间评估如何实施。全文第 20 页指出原始工业数据受保密限制。在组内首先确认可用的数据版本是否含原始时间戳、机器人位置日志和 RT 长度标尺，这三项决定了位置配准能否实证检验。

