# Use the official Odoo 18 base image
FROM odoo:18.0

# Set the working directory container-side
USER root

# Copy your custom fund management addon into the Odoo extra-addons directory
COPY ./ /mnt/extra-addons/fund_management

# Switch back to the unprivileged odoo user for security
USER odoo