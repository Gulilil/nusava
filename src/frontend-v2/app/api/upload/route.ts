import { NextResponse } from "next/server";
import { v2 as cloudinary } from 'cloudinary';
// import path from "path";
// import { writeFile, mkdir } from "fs/promises";

cloudinary.config({
  cloud_name: process.env.CLOUDINARY_CLOUD_NAME,
  api_key: process.env.CLOUDINARY_API_KEY,
  api_secret: process.env.CLOUDINARY_API_SECRET,
});

// export const POST = async (req: Request) => {
//   try {
//     const formData = await req.formData();

//     const file = formData.get("file") as File;
//     if (!file) {
//       return NextResponse.json({ error: "No files received." }, { status: 400 });
//     }

//     const buffer = Buffer.from(await file.arrayBuffer());
//     const filename = Date.now() + "_" + file.name.replaceAll(" ", "_");
//     const projectRoot = path.join(process.cwd(), '..', '..')
//     const sharedUploadsDir = path.join(projectRoot, 'src/shared-uploads')
    
//     // Ensure directory exists
//     await mkdir(sharedUploadsDir, { recursive: true })
//     // Save to shared directory
//     const sharedPath = path.join(sharedUploadsDir, filename)
//     await writeFile(sharedPath, buffer)

//     // Also save to public for frontend preview
//     const publicDir = path.join(process.cwd(), 'public', 'uploads')
//     await mkdir(publicDir, { recursive: true })
//     const publicPath = path.join(publicDir, filename)
//     await writeFile(publicPath, buffer)

//     return NextResponse.json({
//       message: "Success",
//       filename: filename,
//       localPath: sharedPath,
//       url: `/uploads/${filename}`
//     }, { status: 201 });
//   } catch (error) {
//     console.log("Error occurred ", error);
//     return NextResponse.json({ message: "Failed", error: error }, { status: 500 });
//   }
// };

export const POST = async (req: Request) => {
  try {
    const formData = await req.formData();

    const file = formData.get("file") as File;
    if (!file) {
      return NextResponse.json({ error: "No files received." }, { status: 400 });
    }

    const buffer = Buffer.from(await file.arrayBuffer());
    
    // Upload to Cloudinary
    const uploadResponse = await new Promise((resolve, reject) => {
      cloudinary.uploader.upload_stream(
        {
          resource_type: "auto",
          folder: "nusava-posts", // Organize uploads in a folder
          public_id: `${Date.now()}_${file.name.replaceAll(" ", "_")}`,
        },
        (error, result) => {
          if (error) reject(error);
          else resolve(result);
        }
      ).end(buffer);
    });

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const result = uploadResponse as any;

    return NextResponse.json({ 
      message: "Success", 
      filename: result.public_id,
      url: result.secure_url,
      width: result.width,
      height: result.height
    }, { status: 201 });
  } catch (error) {
    console.log("Error occurred ", error);
    return NextResponse.json({ message: "Failed", error: error }, { status: 500 });
  }
};